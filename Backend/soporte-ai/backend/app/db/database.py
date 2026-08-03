from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# db.py
import mysql.connector

DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/soporte_ai"

engine = create_engine(
    DATABASE_URL,
    echo=True,              # 👈 Muestra queries SQL (debug)
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="soporte_ai"
    )