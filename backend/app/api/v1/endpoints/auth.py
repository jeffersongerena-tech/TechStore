from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_roles
from app.database.connection import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import LoginRequest, TokenResponse, UsuarioCreate, UsuarioOut, UsuarioUpdate
from app.services.auth_service import AuthService

router = APIRouter()


@router.post(
    "/auth/login",
    response_model=TokenResponse,
    tags=["Autenticación y Usuarios"],
    summary="Iniciar sesión y obtener token JWT",
)
def iniciar_sesion(payload: LoginRequest, db: Session = Depends(get_db)):
    return AuthService(db).login(payload)


@router.get(
    "/auth/me",
    response_model=UsuarioOut,
    tags=["Autenticación y Usuarios"],
    summary="Consultar perfil del usuario autenticado",
)
def perfil_actual(usuario: Usuario = Depends(get_current_user)):
    return usuario


@router.post(
    "/usuarios",
    response_model=UsuarioOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Autenticación y Usuarios"],
    summary="Registrar nuevo usuario (solo Administrador)",
)
def crear_usuario(
    payload: UsuarioCreate,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(require_roles("ADMINISTRADOR")),
):
    return AuthService(db).crear_usuario(payload, id_actor=actor.id_usuario)


@router.get(
    "/usuarios",
    response_model=list[UsuarioOut],
    tags=["Autenticación y Usuarios"],
    summary="Listar usuarios del sistema (solo Administrador)",
)
def listar_usuarios(
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles("ADMINISTRADOR")),
):
    return AuthService(db).listar_usuarios()


@router.put(
    "/usuarios/{id_usuario}",
    response_model=UsuarioOut,
    tags=["Autenticación y Usuarios"],
    summary="Actualizar rol, nombre o estado de un usuario",
)
def actualizar_usuario(
    id_usuario: int,
    payload: UsuarioUpdate,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(require_roles("ADMINISTRADOR")),
):
    return AuthService(db).actualizar_usuario(id_usuario, payload, id_actor=actor.id_usuario)
