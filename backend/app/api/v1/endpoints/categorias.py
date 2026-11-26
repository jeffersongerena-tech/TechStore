from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_roles
from app.database.connection import get_db
from app.models.usuario import Usuario
from app.schemas.categoria import CategoriaCreate, CategoriaOut, CategoriaUpdate
from app.services.categoria_service import CategoriaService

router = APIRouter(prefix="/categorias", tags=["1. Categorías"])


@router.post(
    "",
    response_model=CategoriaOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar una nueva categoría",
)
def registrar_categoria(
    payload: CategoriaCreate,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(require_roles("ADMINISTRADOR")),
):
    return CategoriaService(db).registrar(payload, id_usuario=actor.id_usuario)


@router.get(
    "",
    response_model=list[CategoriaOut],
    summary="Listar categorías con filtro opcional",
)
def listar_categorias(
    solo_activas: bool = Query(default=False, description="Si es true devuelve únicamente categorías activas"),
    q: str | None = Query(default=None, description="Texto para buscar por nombre"),
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return CategoriaService(db).listar(solo_activas=solo_activas, q=q)


@router.get(
    "/{id_categoria}",
    response_model=CategoriaOut,
    summary="Consultar una categoría por su ID",
)
def consultar_categoria(
    id_categoria: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return CategoriaService(db).consultar(id_categoria)


@router.put(
    "/{id_categoria}",
    response_model=CategoriaOut,
    summary="Actualizar una categoría existente",
)
def actualizar_categoria(
    id_categoria: int,
    payload: CategoriaUpdate,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(require_roles("ADMINISTRADOR")),
):
    return CategoriaService(db).actualizar(id_categoria, payload, id_usuario=actor.id_usuario)


@router.patch(
    "/{id_categoria}/desactivar",
    response_model=CategoriaOut,
    summary="Desactivar lógicamente una categoría",
)
def desactivar_categoria(
    id_categoria: int,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(require_roles("ADMINISTRADOR")),
):
    return CategoriaService(db).desactivar(id_categoria, id_usuario=actor.id_usuario)
