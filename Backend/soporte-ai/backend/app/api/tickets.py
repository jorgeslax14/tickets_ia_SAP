import json

from fastapi import APIRouter, HTTPException

from app.db.database import get_connection
from app.services.ai_service import analyze_ticket
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

    # 1. Análisis con IA (con fallback si la IA falla o responde algo no parseable)
    try:
        parsed = json.loads(analyze_ticket(message))
    except Exception:
        parsed = FALLBACK_ANALYSIS

    # 2. Prioridad
    priority = calculate_priority(
        parsed.get("urgencia", FALLBACK_ANALYSIS["urgencia"]),
        parsed.get("impacto", FALLBACK_ANALYSIS["impacto"]),
    )

    # 3. INSERT en MySQL
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
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM tickets ORDER BY priority DESC")
        tickets = cursor.fetchall()

        cursor.close()
        conn.close()

        return {"success": True, "data": tickets}

    except Exception as e:
        return {"success": False, "message": str(e)}


@router.put("/tickets/{ticket_id}")
def update_ticket_status(ticket_id: int, data: dict):
    new_status = data.get("status")
    if new_status not in ALLOWED_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"'status' debe ser uno de {sorted(ALLOWED_STATUSES)}",
        )

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE tickets SET status = %s WHERE id = %s",
            (new_status, ticket_id),
        )
        conn.commit()

        updated = cursor.rowcount > 0

        cursor.close()
        conn.close()

        if not updated:
            raise HTTPException(status_code=404, detail="Ticket no encontrado")

        return {"success": True, "message": f"Ticket actualizado a {new_status}"}

    except HTTPException:
        raise
    except Exception as e:
        return {"success": False, "message": str(e)}
