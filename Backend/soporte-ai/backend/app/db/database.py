import os
from dotenv import load_dotenv
import mysql.connector
import pyodbc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

SQL_ECHO = os.getenv("SQL_ECHO", "false").lower() == "true"

# ----------------------------------------------------
# 1. Conexión a MySQL 🐬
# ----------------------------------------------------
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
DB_NAME = os.getenv("DB_NAME", "soporte_ai")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(
    DATABASE_URL,
    echo=SQL_ECHO,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_connection():
    """Conexión directa a MySQL usando conector nativo"""
    return mysql.connector.connect(
        host=DB_HOST,
        port=int(DB_PORT),
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

# ----------------------------------------------------
# 2. Conexión a SQL Server 🪟
# ----------------------------------------------------
SQLDB_SERVER = os.getenv("SQLDB_SERVER", "(localdb)\\MSSQLLocalDB")
SQLDB_NAME = os.getenv("SQLDB_NAME", "soporte_tickets")
SQLDB_DRIVER = os.getenv("SQLDB_DRIVER", "ODBC Driver 17 for SQL Server")

SQLSERVER_DATABASE_URL = (
    f"mssql+pyodbc://@{SQLDB_SERVER}/{SQLDB_NAME}"
    f"?driver={SQLDB_DRIVER.replace(' ', '+')}&trusted_connection=yes"
)

engine_sqlserver = create_engine(
    SQLSERVER_DATABASE_URL,
    echo=SQL_ECHO,
    pool_pre_ping=True
)

SessionLocal_sqlserver = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine_sqlserver
)

def get_sqlserver_connection():
    """Conexión directa a SQL Server mediante pyodbc"""
    conn_str = (
        f"DRIVER={{{SQLDB_DRIVER}}};"
        f"SERVER={SQLDB_SERVER};"
        f"DATABASE={SQLDB_NAME};"
        "Trusted_Connection=yes;"
    )
    return pyodbc.connect(conn_str)