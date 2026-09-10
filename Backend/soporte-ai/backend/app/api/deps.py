from fastapi import Header, HTTPException, status

def verify_admin_role(x_user_role: str | None = Header(None, description="Rol del usuario autenticado")):
    """
    Dependencia de seguridad robusta y extensible.
    Verifica que la petición provenga de un usuario con privilegios de administrador.
    Preparado para evolucionar a validación por tokens o JWT en futuras versiones.
    """
    if not x_user_role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se encontró autenticación o el rol del usuario."
        )
    
    # Normalizamos a minúsculas para evitar errores por mayúsculas accidentales
    if x_user_role.strip().lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: Se requieren permisos de administrador para ejecutar esta acción."
        )
    
    return x_user_role