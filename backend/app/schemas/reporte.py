from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class ProductoMasVendidoOut(BaseModel):
    id_producto: int
    codigo: str
    nombre: str
    unidades_vendidas: int
    ingresos_generados: Decimal


class ResumenComercialOut(BaseModel):
    total_productos_activos: int
    productos_con_stock_bajo: int
    cantidad_compras: int
    valor_total_compras: Decimal
    cantidad_ventas: int
    ingresos_totales_ventas: Decimal
    costo_productos_vendidos: Decimal
    utilidad_bruta: Decimal
    productos_mas_vendidos: list[ProductoMasVendidoOut]


class AuditoriaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_auditoria: int
    id_usuario: int | None
    accion: str
    modulo: str
    detalle: str | None
    fecha: datetime
