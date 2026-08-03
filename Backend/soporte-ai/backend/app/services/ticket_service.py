from app.db.database import SessionLocal
from app.models.ticket import Ticket

def create_ticket_db(data: dict):
    db = SessionLocal()

    try:
        new_ticket = Ticket(
            title=data.get("title"),
            description=data.get("description"),
            module=data.get("module"),
            transaction_code=data.get("transaction"),
            priority=data.get("priority"),
            status="OPEN",
            created_by=data.get("created_by")
        )

        db.add(new_ticket)
        db.commit()
        db.refresh(new_ticket)

        return new_ticket

    except Exception as e:
        db.rollback()
        print("❌ Error insertando ticket:", e)
        raise e

    finally:
        db.close()