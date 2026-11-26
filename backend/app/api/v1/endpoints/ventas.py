from datetime import date
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import require_roles
from app.database.connection import get_db
from app.models.usuario import Usuario
from app.schemas.venta import VentaCreate, VentaOut
from app.services.venta_service import VentaService

router = APIRouter(prefix="/ventas", tags=["5. Ventas"])


@router.post(
    "",
    response_model=VentaOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar venta validando stock disponible y descontando inventario (ACID)",
)
def registrar_venta(
    payload: VentaCreate,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(require_roles("ADMINISTRADOR", "VENDEDOR")),
):
    return VentaService(db).registrar_venta(payload, id_usuario=actor.id_usuario)


@router.get(
    "",
    response_model=list[VentaOut],
    summary="Listar ventas con filtro por cliente o rango de fechas",
)
def listar_ventas(
    id_cliente: int | None = Query(default=None),
    fecha_desde: date | None = Query(default=None),
    fecha_hasta: date | None = Query(default=None),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles("ADMINISTRADOR", "VENDEDOR")),
):
    return VentaService(db).listar_ventas(
        id_cliente=id_cliente,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )


@router.get(
    "/{id_venta}",
    response_model=VentaOut,
    summary="Consultar una venta y sus detalles por ID",
)
def consultar_venta(
    id_venta: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles("ADMINISTRADOR", "VENDEDOR")),
):
    return VentaService(db).consultar_venta(id_venta)
