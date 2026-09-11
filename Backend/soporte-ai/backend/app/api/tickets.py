import json

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import verify_admin_role
from app.db.database import (
    get_connection,
    row_to_dict,
    rows_to_list,
    get_status_map,
    get_priority_map,
)
from app.services.ai_services import analyze_ticket
from app.services.prioritization import calculate_priority
from app.services.ticket_service import create_ticket_db

router = APIRouter()

FALLBACK_ANALYSIS = {
    "modulo": "FI",
    "transaccion": "ZFI_PRUEBA",
    "urgencia": 3,
    "impacto": 3,
}


def _score_to_priority_id(score: int) -> int:
    """
    Convierte la puntuación bruta (urgencia*2+impacto, rango ~1..15) a un
    priority_id REAL existente en dbo.priorities, usando 3 niveles lógicos.

    Rangos ajustables:
      - score <= 4  → LOW    (prioridad baja)
      - score <= 8  → MEDIUM (prioridad media)
      - score >  8  → HIGH   (prioridad alta)
    """
    pmap = get_priority_map()
    if score <= 1:
        return pmap["LOW"]
    if score <= 3:
        return pmap["MEDIUM"]
    return pmap["HIGH"]


@router.post("/tickets")
def create_ticket(data: dict):
    message = data.get("message")
    if not message:
        raise HTTPException(status_code=400, detail="El campo 'message' es requerido")

    created_by = data.get("created_by", "desconocido")

    try:
        parsed = json.loads(analyze_ticket(message))
    except Exception:
        parsed = FALLBACK_ANALYSIS

    # Calculamos la puntuación bruta y la mapeamos a un priority_id REAL
    # existente en dbo.priorities (LOW / MEDIUM / HIGH, configurable por IDs).
    raw_score = calculate_priority(
        parsed.get("urgencia", FALLBACK_ANALYSIS["urgencia"]),
        parsed.get("impacto", FALLBACK_ANALYSIS["impacto"]),
    )
    priority_id = _score_to_priority_id(raw_score)

    status_ids = get_status_map()
    if "OPEN" not in status_ids:
        raise HTTPException(
            status_code=500,
            detail=f"No existe el estado 'OPEN' en la tabla dbo.status. Estados disponibles: {sorted(list(status_ids.keys()))}",
        )

    # Insertamos utilizando el modelo relacional exacto de la tabla tickets (status_id, priority_id)
    ticket = create_ticket_db({
        "title": message[:50],
        "description": message,
        "module": parsed.get("modulo", FALLBACK_ANALYSIS["modulo"]),
        "transaction_code": parsed.get("transaccion", FALLBACK_ANALYSIS["transaccion"]),
        "status_id": status_ids["OPEN"],
        "priority_id": priority_id,
        "created_by": created_by,
    })

    return {
        "status": "OK",
        "ticket_id": getattr(ticket, "id", ticket.get("id")),
        "priority_id": priority_id,
    }


@router.get("/tickets")
def get_tickets():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Consultamos ordenando por el id de prioridad relacional
        cursor.execute("SELECT * FROM tickets ORDER BY priority_id DESC")
        tickets = rows_to_list(cursor, cursor.fetchall())

        cursor.close()
        conn.close()

        return {"success": True, "data": tickets}

    except Exception as e:
        return {"success": False, "message": str(e)}


@router.get("/tickets/history")
def get_ticket_history():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM ticket_history ORDER BY created_at DESC")
        rows = rows_to_list(cursor, cursor.fetchall())

        cursor.close()
        conn.close()

        history = []
        for row in rows:
            try:
                parsed_action = json.loads(row["action"])
            except (TypeError, json.JSONDecodeError):
                parsed_action = {"event": row["action"], "ticket": {}}

            history.append({
                "id": row["id"],
                "ticket_id": row["ticket_id"],
                "archived_at": row["created_at"],
                "event": parsed_action.get("event"),
                "ticket": parsed_action.get("ticket", {}),
            })

        return {"success": True, "data": history}

    except Exception as e:
        return {"success": False, "message": str(e)}


def _archive_and_delete_ticket(cursor, ticket: dict):
    """Guarda una foto del ticket en ticket_history y lo borra de tickets."""
    snapshot = json.dumps({"event": "DONE_DELETED", "ticket": ticket}, default=str)
    cursor.execute(
        "INSERT INTO ticket_history (ticket_id, action) VALUES (?, ?)",
        (ticket["id"], snapshot),
    )
    cursor.execute("DELETE FROM tickets WHERE id = ?", (ticket["id"],))


@router.put("/tickets/{ticket_id}")
def update_ticket_status(ticket_id: int, data: dict):
    new_status = data.get("status") # Puede venir como texto (ej. "DONE", "IN_PROGRESS")

    status_ids = get_status_map()

    # Mapeamos a su respectivo ID relacional
    if new_status is None or new_status.upper() not in status_ids:
        raise HTTPException(
            status_code=400,
            detail=f"'status' debe ser uno de {sorted(list(status_ids.keys()))}",
        )

    new_status_id = status_ids[new_status.upper()]

    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
        ticket = row_to_dict(cursor, cursor.fetchone())

        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket no encontrado")

        if new_status == "DONE":
            _archive_and_delete_ticket(cursor, ticket)
            message = "Ticket finalizado y movido a ticket_history"
        else:
            # Actualizamos utilizando status_id en lugar de texto plano
            cursor.execute(
                "UPDATE tickets SET status_id = ? WHERE id = ?",
                (new_status_id, ticket_id),
            )
            message = f"Ticket actualizado a {new_status}"

        conn.commit()
        cursor.close()

        return {"success": True, "message": message}

    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": str(e)}
    finally:
        conn.close()


@router.put("/tickets/{ticket_id}/assign")
def assign_ticket(
    ticket_id: int, 
    data: dict, 
    admin_role: str = Depends(verify_admin_role)
):
    """
    BE-008: Autorización Server-Side.
    Valida mediante la dependencia 'verify_admin_role' que el usuario que llama
    tenga privilegios de administrador antes de asignar el ticket.
    """
    assigned_to = data.get("assigned_to")
    if assigned_to is None:
        raise HTTPException(status_code=400, detail="El campo 'assigned_to' es requerido")

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE tickets SET assigned_to = ? WHERE id = ?",
            (assigned_to, ticket_id),
        )
        conn.commit()

        updated = cursor.rowcount > 0

        cursor.close()
        conn.close()

        if not updated:
            raise HTTPException(status_code=404, detail="Ticket no encontrado")

        return {
            "success": True, 
            "message": f"Ticket asignado correctamente por un {admin_role}"
        }

    except HTTPException:
        raise
    except Exception as e:
        return {"success": False, "message": str(e)}
        conn.rollback()
        conn.close()