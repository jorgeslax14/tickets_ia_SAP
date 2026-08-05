from fastapi import APIRouter, HTTPException

from app.db.database import get_connection

router = APIRouter()


@router.post("/login")
def login(data: dict):
    username = (data.get("username") or "").strip()
    if not username:
        raise HTTPException(status_code=400, detail="El campo 'username' es requerido")

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT id, name, email, role FROM users WHERE name = %s OR email = %s LIMIT 1",
            (username, username),
        )
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        return {"success": True, "data": user}

    except HTTPException:
        raise
    except Exception as e:
        return {"success": False, "message": str(e)}
