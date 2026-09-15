from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base
import datetime

Base = declarative_base()

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text)
    description = Column(Text)
    module = Column(String(50))
    transaction_code = Column(String(20))
    
    # Columnas relacionales exactas que tienes en SQL Server
    status_id = Column(Integer)
    priority_id = Column(Integer)
    assigned_to = Column(String(50), nullable=True)
    
    created_by = Column(String(50))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)