from app.db.database import SessionLocal
from app.models.ticket import Ticket


def create_ticket_db(data: dict):
    db = SessionLocal()

    ticket_data = dict(
        title=data.get("title"),
        description=data.get("description"),
        module=data.get("module"),
        transaction_code=data.get("transaction"),
        priority=data.get("priority"),
        status="OPEN",
        created_by=data.get("created_by")
    )

    try:
        ticket = Ticket(**ticket_data)
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        return ticket
    except Exception as error:
        db.rollback()
        print("❌ Error creando ticket en SQL Server:", error)
        raise error
    finally:
        db.close()
