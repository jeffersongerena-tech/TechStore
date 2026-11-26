from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_roles
from app.database.connection import get_db
from app.models.usuario import Usuario
from app.schemas.producto import ExistenciaProductoOut, ProductoCreate, ProductoOut, ProductoUpdate
from app.services.producto_service import ProductoService

router = APIRouter(prefix="/productos", tags=["2. Productos"])


@router.post(
    "",
    response_model=ProductoOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo producto",
)
def registrar_producto(
    payload: ProductoCreate,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(require_roles("ADMINISTRADOR")),
):
    return ProductoService(db).registrar(payload, id_usuario=actor.id_usuario)


@router.get(
    "",
    response_model=list[ProductoOut],
    summary="Listar productos con búsqueda y filtros",
)
def listar_productos(
    id_categoria: int | None = Query(default=None),
    solo_activos: bool = Query(default=False),
    q: str | None = Query(default=None, description="Buscar por código o nombre"),
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return ProductoService(db).listar(id_categoria=id_categoria, solo_activos=solo_activos, q=q)


@router.get(
    "/existencias/resumen",
    response_model=list[ExistenciaProductoOut],
    summary="Consultar existencias de todo el catálogo",
)
def listar_existencias_productos(
    solo_activos: bool = Query(default=True),
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return ProductoService(db).listar_existencias(solo_activos=solo_activos)


@router.get(
    "/{id_producto}",
    response_model=ProductoOut,
    summary="Consultar detalle de un producto por ID",
)
def consultar_producto(
    id_producto: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return ProductoService(db).consultar(id_producto)


@router.get(
    "/{id_producto}/existencias",
    response_model=ExistenciaProductoOut,
    summary="Consultar existencias disponibles y estado de stock de un producto",
)
def consultar_existencias_producto(
    id_producto: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return ProductoService(db).consultar_existencia(id_producto)


@router.put(
    "/{id_producto}",
    response_model=ProductoOut,
    summary="Actualizar información, precios o stock mínimo de un producto",
)
def actualizar_producto(
    id_producto: int,
    payload: ProductoUpdate,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(require_roles("ADMINISTRADOR")),
):
    return ProductoService(db).actualizar(id_producto, payload, id_usuario=actor.id_usuario)


@router.patch(
    "/{id_producto}/desactivar",
    response_model=ProductoOut,
    summary="Desactivar un producto sin borrar su historial",
)
def desactivar_producto(
    id_producto: int,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(require_roles("ADMINISTRADOR")),
):
    return ProductoService(db).desactivar(id_producto, id_usuario=actor.id_usuario)
