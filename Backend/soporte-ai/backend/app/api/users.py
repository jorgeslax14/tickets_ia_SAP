from fastapi import APIRouter, HTTPException
from app.db.database import get_connection, row_to_dict, rows_to_list
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get("/users")
def get_users(role: str | None = None):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Usamos JOIN con la tabla roles para obtener el nombre del rol (ej. 'admin' o 'user')
        if role:
            cursor.execute(
                """
                SELECT u.id, u.name, u.email, r.name as role 
                FROM Users u
                JOIN roles r ON u.role_id = r.id
                WHERE r.name = ?
                """,
                (role,),
            )
        else:
            cursor.execute(
                """
                SELECT u.id, u.name, u.email, r.name as role 
                FROM Users u
                JOIN roles r ON u.role_id = r.id
                """
            )

        users = rows_to_list(cursor, cursor.fetchall())

        cursor.close()
        conn.close()
        return {"success": True, "data": users}
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.post("/users")
def create_user(data: dict):
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    password = (data.get("password") or "").strip()
    
    # Recibimos el role_id numérico (por defecto 2 para 'user', o el que envíen)
    role_id = data.get("role_id") or 2

    if not name or not email or not password:
        raise HTTPException(
            status_code=400, 
            detail="Nombre, correo y contraseña son obligatorios"
        )

    # El backend genera el hash automáticamente de forma segura
    password_hash = pwd_context.hash(password)

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO Users (name, email, password_hash, role_id) VALUES (?, ?, ?, ?)",
            (name, email, password_hash, role_id)
        )
        conn.commit()
        
        cursor.close()
        conn.close()

        return {
            "success": True, 
            "message": "Usuario creado exitosamente con contraseña encriptada"
        }

    except Exception as e:
        return {"success": False, "message": str(e)}


@router.post("/login")
def login(data: dict):
    username = (data.get("username") or data.get("name") or "").strip()
    password = (data.get("password") or "").strip()

    if not username or not password:
        raise HTTPException(status_code=400, detail="Usuario y contraseña son requeridos")

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Realizamos el JOIN con roles para extraer el nombre del rol asociado al usuario
        cursor.execute(
            """
            SELECT TOP 1 u.id, u.name, u.email, u.password_hash, r.name as role 
            FROM Users u
            JOIN roles r ON u.role_id = r.id
            WHERE u.name = ? OR u.email = ?
            """,
            (username, username),
        )
        user = row_to_dict(cursor, cursor.fetchone())

        cursor.close()
        conn.close()

        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        if not user.get("password_hash"):
            raise HTTPException(
                status_code=401,
                detail="El usuario no tiene contraseña configurada"
            )

        if not pwd_context.verify(password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Contraseña incorrecta")

        user.pop("password_hash", None)

        return {"success": True, "data": user}

    except HTTPException:
        raise
    except Exception as e:
        return {"success": False, "message": str(e)}