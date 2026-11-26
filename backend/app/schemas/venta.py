from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class DetalleVentaIn(BaseModel):
    id_producto: int = Field(..., gt=0)
    cantidad: int = Field(..., gt=0, description="Cantidad vendida estrictamente mayor que cero")
    precio_unitario: Decimal | None = Field(
        default=None,
        ge=Decimal("0.00"),
        description="Opcional: si se omite se toma el precio_venta vigente del producto",
    )
    descuento: Decimal = Field(
        default=Decimal("0.00"),
        ge=Decimal("0.00"),
        description="Descuento aplicado a esta línea de producto",
    )


class VentaCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    id_cliente: int = Field(..., gt=0)
    descuento_adicional: Decimal = Field(default=Decimal("0.00"), ge=Decimal("0.00"))
    porcentaje_impuesto: Decimal = Field(
        default=Decimal("0.00"),
        ge=Decimal("0.00"),
        le=Decimal("100.00"),
        description="Porcentaje de impuesto (ej. 19 para IVA 19%, o 0 si no aplica)",
    )
    impuesto_fijo: Decimal | None = Field(default=None, ge=Decimal("0.00"))
    observacion: str | None = Field(default=None, max_length=255)
    detalles: list[DetalleVentaIn] = Field(..., min_length=1, description="Al menos un producto en la venta")


class DetalleVentaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_detalle_venta: int
    id_producto: int
    cantidad: int
    precio_unitario: Decimal
    descuento: Decimal
    subtotal: Decimal


class VentaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_venta: int
    id_cliente: int
    id_usuario: int
    fecha: datetime
    subtotal: Decimal
    descuento: Decimal
    impuesto: Decimal
    total: Decimal
    estado: str
    detalles: list[DetalleVentaOut]
