from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_roles
from app.database.connection import get_db
from app.models.usuario import Usuario
from app.schemas.terceros import (
    ClienteCreate,
    ClienteOut,
    ClienteUpdate,
    ProveedorCreate,
    ProveedorOut,
    ProveedorUpdate,
)
from app.services.terceros_service import ClienteService, ProveedorService

router = APIRouter(tags=["3. Proveedores y Clientes"])


# ----------------------------- PROVEEDORES -----------------------------
@router.post(
    "/proveedores",
    response_model=ProveedorOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un proveedor",
)
def registrar_proveedor(
    payload: ProveedorCreate,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(require_roles("ADMINISTRADOR", "ENCARGADO_INVENTARIO")),
):
    return ProveedorService(db).registrar(payload, id_usuario=actor.id_usuario)


@router.get(
    "/proveedores",
    response_model=list[ProveedorOut],
    summary="Listar y buscar proveedores",
)
def listar_proveedores(
    solo_activos: bool = Query(default=False),
    q: str | None = Query(default=None, description="Buscar por NIT o nombre"),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles("ADMINISTRADOR", "ENCARGADO_INVENTARIO")),
):
    return ProveedorService(db).listar(solo_activos=solo_activos, q=q)


@router.get(
    "/proveedores/{id_proveedor}",
    response_model=ProveedorOut,
    summary="Consultar un proveedor por ID",
)
def consultar_proveedor(
    id_proveedor: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles("ADMINISTRADOR", "ENCARGADO_INVENTARIO")),
):
    return ProveedorService(db).consultar(id_proveedor)


@router.put(
    "/proveedores/{id_proveedor}",
    response_model=ProveedorOut,
    summary="Actualizar datos de un proveedor",
)
def actualizar_proveedor(
    id_proveedor: int,
    payload: ProveedorUpdate,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(require_roles("ADMINISTRADOR", "ENCARGADO_INVENTARIO")),
):
    return ProveedorService(db).actualizar(id_proveedor, payload, id_usuario=actor.id_usuario)


# ------------------------------ CLIENTES ------------------------------
@router.post(
    "/clientes",
    response_model=ClienteOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un cliente",
)
def registrar_cliente(
    payload: ClienteCreate,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(require_roles("ADMINISTRADOR", "VENDEDOR")),
):
    return ClienteService(db).registrar(payload, id_usuario=actor.id_usuario)


@router.get(
    "/clientes",
    response_model=list[ClienteOut],
    summary="Listar y buscar clientes",
)
def listar_clientes(
    solo_activos: bool = Query(default=False),
    q: str | None = Query(default=None, description="Buscar por documento o nombre"),
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return ClienteService(db).listar(solo_activos=solo_activos, q=q)


@router.get(
    "/clientes/{id_cliente}",
    response_model=ClienteOut,
    summary="Consultar un cliente por ID",
)
def consultar_cliente(
    id_cliente: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return ClienteService(db).consultar(id_cliente)


@router.put(
    "/clientes/{id_cliente}",
    response_model=ClienteOut,
    summary="Actualizar datos de un cliente",
)
def actualizar_cliente(
    id_cliente: int,
    payload: ClienteUpdate,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(require_roles("ADMINISTRADOR", "VENDEDOR")),
):
    return ClienteService(db).actualizar(id_cliente, payload, id_usuario=actor.id_usuario)
