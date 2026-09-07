import os
from dotenv import load_dotenv
import pyodbc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

SQL_ECHO = os.getenv("SQL_ECHO", "false").lower() == "true"

SQLDB_SERVER = os.getenv("SQLDB_SERVER", "02-5CD4284C3V")
SQLDB_NAME = os.getenv("SQLDB_NAME", "soporte_sap_ia")
SQLDB_DRIVER = os.getenv("SQLDB_DRIVER", "ODBC Driver 17 for SQL Server")
SQLDB_TRUSTED = os.getenv("SQLDB_TRUSTED", "yes").lower() == "yes"
SQLDB_USER = os.getenv("SQLDB_USER", "")
SQLDB_PASSWORD = os.getenv("SQLDB_PASSWORD", "")

if SQLDB_TRUSTED:
    SQLSERVER_DATABASE_URL = (
        f"mssql+pyodbc://@{SQLDB_SERVER}/{SQLDB_NAME}"
        f"?driver={SQLDB_DRIVER.replace(' ', '+')}&trusted_connection=yes"
    )
else:
    SQLSERVER_DATABASE_URL = (
        f"mssql+pyodbc://{SQLDB_USER}:{SQLDB_PASSWORD}@{SQLDB_SERVER}/{SQLDB_NAME}"
        f"?driver={SQLDB_DRIVER.replace(' ', '+')}"
    )

engine = create_engine(
    SQLSERVER_DATABASE_URL,
    echo=SQL_ECHO,
    pool_pre_ping=True,
    future=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True
)


def get_connection():
    """Conexión directa a SQL Server mediante pyodbc 🪟"""
    if SQLDB_TRUSTED:
        conn_str = (
            f"DRIVER={{{SQLDB_DRIVER}}};"
            f"SERVER={SQLDB_SERVER};"
            f"DATABASE={SQLDB_NAME};"
            "Trusted_Connection=yes;"
        )
    else:
        conn_str = (
            f"DRIVER={{{SQLDB_DRIVER}}};"
            f"SERVER={SQLDB_SERVER};"
            f"DATABASE={SQLDB_NAME};"
            f"UID={SQLDB_USER};"
            f"PWD={SQLDB_PASSWORD};"
        )
    return pyodbc.connect(conn_str)


def row_to_dict(cursor, row):
    """Convierte una fila pyodbc a diccionario usando los nombres de columna."""
    if row is None:
        return None
    columns = [column[0] for column in cursor.description]
    return dict(zip(columns, row))


def rows_to_list(cursor, rows):
    """Convierte una lista de filas pyodbc a lista de diccionarios."""
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in rows]
