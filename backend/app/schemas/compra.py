from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class DetalleCompraIn(BaseModel):
    id_producto: int = Field(..., gt=0)
    cantidad: int = Field(..., gt=0, description="Cantidad comprada estrictamente mayor que cero")
    costo_unitario: Decimal = Field(..., ge=Decimal("0.00"), description="Costo unitario no negativo")


class CompraCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    id_proveedor: int = Field(..., gt=0)
    observacion: str | None = Field(default=None, max_length=255)
    detalles: list[DetalleCompraIn] = Field(..., min_length=1, description="Al menos un producto en la compra")


class DetalleCompraOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_detalle_compra: int
    id_producto: int
    cantidad: int
    costo_unitario: Decimal
    subtotal: Decimal


class CompraOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_compra: int
    id_proveedor: int
    id_usuario: int
    fecha: datetime
    total: Decimal
    estado: str
    detalles: list[DetalleCompraOut]
