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
    priority = Column(Integer)
    status = Column(String(50))
    created_by = Column(String(50))