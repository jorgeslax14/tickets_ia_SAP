import json

from fastapi import APIRouter, HTTPException

from app.db.database import get_connection, row_to_dict, rows_to_list
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

ALLOWED_STATUSES = {"OPEN", "IN_PROGRESS", "DONE"}


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

    priority = calculate_priority(
        parsed.get("urgencia", FALLBACK_ANALYSIS["urgencia"]),
        parsed.get("impacto", FALLBACK_ANALYSIS["impacto"]),
    )

    ticket = create_ticket_db({
        "title": message[:50],
        "description": message,
        "module": parsed.get("modulo", FALLBACK_ANALYSIS["modulo"]),
        "transaction": parsed.get("transaccion", FALLBACK_ANALYSIS["transaccion"]),
        "priority": priority,
        "created_by": created_by,
    })

    return {
        "status": "OK",
        "ticket_id": ticket.id,
        "priority": priority,
    }


@router.get("/tickets")
def get_tickets():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM tickets ORDER BY priority DESC")
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
    new_status = data.get("status")
    if new_status not in ALLOWED_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"'status' debe ser uno de {sorted(ALLOWED_STATUSES)}",
        )

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
            cursor.execute(
                "UPDATE tickets SET status = ? WHERE id = ?",
                (new_status, ticket_id),
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
def assign_ticket(ticket_id: int, data: dict):
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

        return {"success": True, "message": "Ticket asignado correctamente"}

    except HTTPException:
        raise
    except Exception as e:
        return {"success": False, "message": str(e)}
