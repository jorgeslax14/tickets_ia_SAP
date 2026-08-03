from fastapi import APIRouter
from app.services.ai_service import analyze_ticket
from app.services.prioritization import calculate_priority
from app.services.ticket_service import create_ticket_db
from app.db.database import get_connection
import json

router = APIRouter()

@router.post("/tickets")
def create_ticket(data: dict):
    message = data["message"]

    # 🔹 1. IA
    ai_raw = analyze_ticket(message)

    try:
        parsed = json.loads(ai_raw)
    except:
        parsed = {
            "modulo": "FI",
            "transaccion": "ZFI_PRUEBA",
            "urgencia": 3,
            "impacto": 3,
            "created_by":"Jorge"
        }

    # 🔹 2. Prioridad
    priority = calculate_priority(
        parsed["urgencia"],
        parsed["impacto"]
    )

    # 🔹 3. INSERT en MySQL
    ticket = create_ticket_db({
        "title": message[:50],
        "description": message,
        "module": parsed["modulo"],
        "transaction": parsed["transaccion"],
        "priority": priority,
        "created_by":parsed["created_by"]
    })

    return {
        "status": "OK",
        "ticket_id": ticket.id,
        "priority": priority
    }

@router.get("/tickets")
def get_tickets():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM tickets ORDER BY priority DESC"
        cursor.execute(query)

        tickets = cursor.fetchall()

        cursor.close()
        conn.close()

        return {
            "success": True,
            "data": tickets
        }

    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

# 🔥 Actualizar estado del ticket
@router.put("/tickets/{ticket_id}")
def update_ticket_status(ticket_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            UPDATE tickets
            SET status = 'IN_PROGRESS'
            WHERE id = %s
        """

        cursor.execute(query, (ticket_id,))
        conn.commit()

        cursor.close()
        conn.close()

        return {
            "success": True,
            "message": "Ticket actualizado a IN_PROGRESS"
        }

    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }