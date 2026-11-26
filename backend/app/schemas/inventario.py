from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

TipoMovimiento = Literal["ENTRADA", "SALIDA"]


class MovimientoCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    id_producto: int = Field(..., gt=0)
    tipo: TipoMovimiento
    cantidad: int = Field(..., gt=0, description="Cantidad del movimiento mayor que cero")
    observacion: str = Field(..., min_length=3, max_length=255, description="Motivo o soporte del movimiento")


class MovimientoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_movimiento: int
    id_producto: int
    id_usuario: int | None
    id_compra: int | None
    id_venta: int | None
    tipo: str
    cantidad: int
    fecha: datetime
    observacion: str | None


class AlertaStockOut(BaseModel):
    id_producto: int
    codigo: str
    nombre: str
    stock_actual: int
    stock_minimo: int
    deficit: int
