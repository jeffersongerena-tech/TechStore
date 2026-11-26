from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import PermisoDenegadoError
from app.core.security import decode_access_token
from app.database.connection import get_db
from app.models.usuario import Usuario

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    """
    Si el cliente envía un token Bearer, valida su firma y carga el usuario real.
    Si no envía token y REQUIRE_AUTH=false (por defecto en Actividad 4), usa el
    usuario Administrador por defecto para facilitar pruebas directas en Swagger/Postman.
    """
    if credentials and credentials.credentials:
        try:
            payload = decode_access_token(credentials.credentials)
            user_id = int(payload.get("sub", "0"))
        except (jwt.PyJWTError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de autenticación inválido o expirado.",
            )
        usuario = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
        if not usuario or not usuario.activo:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario inexistente o desactivado.",
            )
        return usuario

    if settings.REQUIRE_AUTH:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticación requerida. Inicie sesión en /api/v1/auth/login.",
        )

    fallback = (
        db.query(Usuario)
        .filter(Usuario.rol == "ADMINISTRADOR", Usuario.activo.is_(True))
        .order_by(Usuario.id_usuario.asc())
        .first()
    )
    if not fallback:
        fallback = db.query(Usuario).order_by(Usuario.id_usuario.asc()).first()
    if not fallback:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No existe ningún usuario inicializado en la base de datos.",
        )
    return fallback


def require_roles(*roles_permitidos: str):
    def _checker(current_user: Usuario = Depends(get_current_user)) -> Usuario:
        if current_user.rol not in roles_permitidos:
            raise PermisoDenegadoError(
                f"Operación no autorizada para el rol '{current_user.rol}'. "
                f"Roles permitidos: {', '.join(roles_permitidos)}."
            )
        return current_user

    return _checker
