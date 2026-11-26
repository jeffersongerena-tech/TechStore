from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class ProductoCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    codigo: str = Field(..., min_length=2, max_length=30, description="Código único del producto")
    nombre: str = Field(..., min_length=2, max_length=120)
    descripcion: str | None = Field(default=None, max_length=255)
    id_categoria: int = Field(..., gt=0)
    precio_venta: Decimal = Field(..., ge=Decimal("0.00"), description="Precio de venta no negativo")
    costo_actual: Decimal = Field(default=Decimal("0.00"), ge=Decimal("0.00"), description="Costo unitario no negativo")
    stock_actual: int = Field(default=0, ge=0, description="Existencias iniciales no negativas")
    stock_minimo: int = Field(default=5, ge=0, description="Umbral para alerta de stock bajo")


class ProductoUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    codigo: str | None = Field(default=None, min_length=2, max_length=30)
    nombre: str | None = Field(default=None, min_length=2, max_length=120)
    descripcion: str | None = Field(default=None, max_length=255)
    id_categoria: int | None = Field(default=None, gt=0)
    precio_venta: Decimal | None = Field(default=None, ge=Decimal("0.00"))
    costo_actual: Decimal | None = Field(default=None, ge=Decimal("0.00"))
    stock_minimo: int | None = Field(default=None, ge=0)
    activo: bool | None = None


class ProductoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_producto: int
    codigo: str
    nombre: str
    descripcion: str | None
    id_categoria: int
    precio_venta: Decimal
    costo_actual: Decimal
    stock_actual: int
    stock_minimo: int
    stock_bajo: bool
    activo: bool
    creado_en: datetime


class ExistenciaProductoOut(BaseModel):
    id_producto: int
    codigo: str
    nombre: str
    stock_actual: int
    stock_minimo: int
    stock_bajo: bool
    unidades_faltantes: int
    activo: bool
