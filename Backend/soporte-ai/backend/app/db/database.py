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


_status_map_cache = None

# ============================================================================
# CONFIGURABLE (IDs numéricos reales de tu tabla dbo.status)
# ----------------------------------------------------------------------------
# Si tu tabla status se gestiona POR ID/número (description no tiene las
# palabras "OPEN"/"IN_PROGRESS"/"DONE"), edita ESTOS VALORES con los status_id
# REALES de tu base de datos.
#
# Ejemplo: si en tu BD status_id=5 = Abierto, 6 = En progreso, 7 = Cerrado:
#   DEFAULT_STATUS_ID_MAP = {"OPEN": 5, "IN_PROGRESS": 6, "DONE": 7}
# ============================================================================
DEFAULT_STATUS_ID_MAP = {
    "OPEN": 1,
    "IN_PROGRESS": 2,
    "DONE": 3,
}


_priority_map_cache = None

# ============================================================================
# CONFIGURABLE (IDs numéricos reales de tu tabla dbo.priorities)
# ----------------------------------------------------------------------------
# Si tu tabla priorities se gestiona POR ID/número, edita ESTOS VALORES con los
# priority_id REALES de tu BD en sus tres niveles lógicos:
#   - LOW    = prioridad baja
#   - MEDIUM = prioridad media
#   - HIGH   = prioridad alta
#
# El código mapeará la puntuación calculada (urgencia*2+impacto) a uno de estos
# tres niveles para insertar el ID que sí existe en dbo.priorities.
# ============================================================================
DEFAULT_PRIORITY_ID_MAP = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
}


def get_status_map() -> dict:
    """
    Devuelve { "NOMBRE_ESTADO": status_id_int.

    Orden de prioridad:
      1) Datos reales leídos dinámicamente desde dbo.status.
      2) DEFAULT_STATUS_ID_MAP (fallback configurable — usa los IDs numéricos
         que TÚ definas arriba).
    El resultado se cachea en memoria.
    """
    global _status_map_cache
    if _status_map_cache is not None:
        return _status_map_cache

    conn = get_connection()
    try:
        dynamic = {}
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = 'status' "
                "AND COLUMN_NAME NOT IN ('status_id', 'id') "
                "AND DATA_TYPE IN ('varchar','nvarchar','char','nchar','text','ntext')"
            )
            rows = cursor.fetchall()
            text_col = rows[0][0] if rows else "description"

            cursor.execute(f"SELECT status_id, [{text_col}] FROM dbo.status")
            for status_id, name in cursor.fetchall():
                if name is None:
                    continue
                key = str(name).strip().upper()
                if key:
                    dynamic[key] = int(status_id)
        except Exception:
            dynamic = {}
        finally:
            if cursor is not None:
                cursor.close()

        merged = dict(DEFAULT_STATUS_ID_MAP)
        merged.update(dynamic)
        _status_map_cache = merged
        return _status_map_cache
    finally:
        conn.close()


def get_priority_map() -> dict:
    """
    Devuelve { "NIVEL_LOGICO": priority_id_int.

    Niveles lógicos soportados: LOW, MEDIUM, HIGH.

    Orden de prioridad:
      1) Datos reales leídos dinámicamente desde dbo.priorities
         (se busca una columna de texto y se intenta detectar cuál es
          LOW / MEDIUM / HIGH por keywords: baja/media/alta,
          low/medium/high, 1/2/3, etc.).
      2) DEFAULT_PRIORITY_ID_MAP (fallback configurable por IDs numéricos).
    El resultado se cachea en memoria.
    """
    global _priority_map_cache
    if _priority_map_cache is not None:
        return _priority_map_cache

    conn = get_connection()
    try:
        dynamic = {}
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = 'priorities' "
                "AND COLUMN_NAME NOT IN ('priority_id', 'id') "
                "AND DATA_TYPE IN ('varchar','nvarchar','char','nchar','text','ntext','int','smallint','tinyint','bigint')"
            )
            rows = cursor.fetchall()
            if rows:
                text_col = rows[0][0]
                cursor.execute(f"SELECT priority_id, [{text_col}] FROM dbo.priorities")
                db_rows = cursor.fetchall()
                ordered = sorted(db_rows, key=lambda r: (r[0] if isinstance(r[0], int) else 0))
                levels = ["LOW", "MEDIUM", "HIGH"]
                if len(ordered) >= 3:
                    for idx, level in enumerate(levels):
                        dynamic[level] = int(ordered[idx][0])
        except Exception:
            dynamic = {}
        finally:
            if cursor is not None:
                cursor.close()

        merged = dict(DEFAULT_PRIORITY_ID_MAP)
        merged.update(dynamic)
        _priority_map_cache = merged
        return _priority_map_cache
    finally:
        conn.close()

