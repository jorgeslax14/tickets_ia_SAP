from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text)
    description = Column(Text)
    module = Column(String(50))
    transaction_code = Column(String(20))
    priority_id = Column(Integer)
    status_id = Column(Integer)
    created_by = Column(String(50))