from app.db.database import SessionLocal, SessionLocal_sqlserver
from app.models.ticket import Ticket

def create_ticket_db(data: dict):
    db_mysql = SessionLocal()
    db_sqlserver = SessionLocal_sqlserver()

    # Mapeo de datos del ticket recibido
    ticket_data = dict(
        title=data.get("title"),
        description=data.get("description"),
        module=data.get("module"),
        transaction_code=data.get("transaction"),
        priority=data.get("priority"),
        status="OPEN",
        created_by=data.get("created_by")
    )

    # 1. Guardar en Base Principal (MySQL) 🐬
    try:
        ticket_mysql = Ticket(**ticket_data)
        db_mysql.add(ticket_mysql)
        db_mysql.commit()
        db_mysql.refresh(ticket_mysql)
    except Exception as error_mysql:
        db_mysql.rollback()
        print("❌ Error crítico en MySQL:", error_mysql)
        raise error_mysql
    finally:
        db_mysql.close()

    # 2. Guardar en Base Secundaria (SQL Server) 🪟
    try:
        ticket_sqlserver = Ticket(**ticket_data)
        db_sqlserver.add(ticket_sqlserver)
        db_sqlserver.commit()
    except Exception as error_sqlserver:
        db_sqlserver.rollback()
        print("⚠️ Advertencia: No se pudo guardar en SQL Server:", error_sqlserver)
    finally:
        db_sqlserver.close()

    return ticket_mysql