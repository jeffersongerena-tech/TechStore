from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_roles
from app.database.connection import get_db
from app.models.usuario import Usuario
from app.schemas.inventario import AlertaStockOut, MovimientoCreate, MovimientoOut
from app.services.inventario_service import InventarioService

router = APIRouter(prefix="/inventario", tags=["6. Inventario y Alertas"])


@router.post(
    "/movimientos",
    response_model=MovimientoOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar movimiento manual de entrada o salida en inventario (ACID)",
)
def registrar_movimiento_inventario(
    payload: MovimientoCreate,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(require_roles("ADMINISTRADOR", "ENCARGADO_INVENTARIO")),
):
    return InventarioService(db).registrar_ajuste(payload, id_usuario=actor.id_usuario)


@router.get(
    "/movimientos",
    response_model=list[MovimientoOut],
    summary="Consultar kardex de movimientos de inventario",
)
def listar_movimientos_inventario(
    id_producto: int | None = Query(default=None),
    tipo: str | None = Query(default=None, description="ENTRADA o SALIDA"),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles("ADMINISTRADOR", "ENCARGADO_INVENTARIO")),
):
    return InventarioService(db).listar_movimientos(id_producto=id_producto, tipo=tipo)


@router.get(
    "/alertas-stock-bajo",
    response_model=list[AlertaStockOut],
    summary="Consultar productos activos con stock igual o inferior al mínimo",
)
def consultar_alertas_stock_bajo(
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return InventarioService(db).consultar_alertas_stock_bajo()
