from datetime import date
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import require_roles
from app.database.connection import get_db
from app.models.usuario import Usuario
from app.schemas.compra import CompraCreate, CompraOut
from app.services.compra_service import CompraService

router = APIRouter(prefix="/compras", tags=["4. Compras"])


@router.post(
    "",
    response_model=CompraOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar compra con detalles e incrementar stock automáticamente (ACID)",
)
def registrar_compra(
    payload: CompraCreate,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(require_roles("ADMINISTRADOR", "ENCARGADO_INVENTARIO")),
):
    return CompraService(db).registrar_compra(payload, id_usuario=actor.id_usuario)


@router.get(
    "",
    response_model=list[CompraOut],
    summary="Listar compras con filtro por proveedor o rango de fechas",
)
def listar_compras(
    id_proveedor: int | None = Query(default=None),
    fecha_desde: date | None = Query(default=None),
    fecha_hasta: date | None = Query(default=None),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles("ADMINISTRADOR", "ENCARGADO_INVENTARIO")),
):
    return CompraService(db).listar_compras(
        id_proveedor=id_proveedor,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )


@router.get(
    "/{id_compra}",
    response_model=CompraOut,
    summary="Consultar una compra y sus líneas de detalle por ID",
)
def consultar_compra(
    id_compra: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles("ADMINISTRADOR", "ENCARGADO_INVENTARIO")),
):
    return CompraService(db).consultar_compra(id_compra)
