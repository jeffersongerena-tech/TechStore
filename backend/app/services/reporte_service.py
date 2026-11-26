from decimal import Decimal
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.compra import Compra
from app.models.producto import Producto
from app.models.venta import DetalleVenta, Venta
from app.repositories.auditoria_repo import AuditoriaRepository
from app.schemas.reporte import ProductoMasVendidoOut, ResumenComercialOut


class ReporteService:
    def __init__(self, db: Session):
        self.db = db
        self.audit = AuditoriaRepository(db)

    def obtener_resumen(self) -> ResumenComercialOut:
        total_activos = self.db.query(func.count(Producto.id_producto)).filter(Producto.activo.is_(True)).scalar() or 0
        stock_bajo = (
            self.db.query(func.count(Producto.id_producto))
            .filter(Producto.activo.is_(True), Producto.stock_actual <= Producto.stock_minimo)
            .scalar()
            or 0
        )

        cant_compras, total_compras = self.db.query(
            func.count(Compra.id_compra),
            func.coalesce(func.sum(Compra.total), 0),
        ).one()

        cant_ventas, ingresos_ventas = self.db.query(
            func.count(Venta.id_venta),
            func.coalesce(func.sum(Venta.total), 0),
        ).one()

        costo_vendido = (
            self.db.query(
                func.coalesce(func.sum(DetalleVenta.cantidad * Producto.costo_actual), 0)
            )
            .join(Producto, Producto.id_producto == DetalleVenta.id_producto)
            .scalar()
            or Decimal("0.00")
        )

        ingresos_dec = Decimal(str(ingresos_ventas)).quantize(Decimal("0.01"))
        compras_dec = Decimal(str(total_compras)).quantize(Decimal("0.01"))
        costo_dec = Decimal(str(costo_vendido)).quantize(Decimal("0.01"))
        utilidad_bruta = (ingresos_dec - costo_dec).quantize(Decimal("0.01"))

        top_rows = (
            self.db.query(
                Producto.id_producto,
                Producto.codigo,
                Producto.nombre,
                func.sum(DetalleVenta.cantidad).label("unidades"),
                func.sum(DetalleVenta.subtotal).label("ingresos"),
            )
            .join(DetalleVenta, DetalleVenta.id_producto == Producto.id_producto)
            .group_by(Producto.id_producto, Producto.codigo, Producto.nombre)
            .order_by(func.sum(DetalleVenta.cantidad).desc())
            .limit(10)
            .all()
        )

        mas_vendidos = [
            ProductoMasVendidoOut(
                id_producto=r.id_producto,
                codigo=r.codigo,
                nombre=r.nombre,
                unidades_vendidas=int(r.unidades or 0),
                ingresos_generados=Decimal(str(r.ingresos or 0)).quantize(Decimal("0.01")),
            )
            for r in top_rows
        ]

        return ResumenComercialOut(
            total_productos_activos=int(total_activos),
            productos_con_stock_bajo=int(stock_bajo),
            cantidad_compras=int(cant_compras or 0),
            valor_total_compras=compras_dec,
            cantidad_ventas=int(cant_ventas or 0),
            ingresos_totales_ventas=ingresos_dec,
            costo_productos_vendidos=costo_dec,
            utilidad_bruta=utilidad_bruta,
            productos_mas_vendidos=mas_vendidos,
        )

    def listar_auditoria(self, modulo: str | None = None, limit: int = 100):
        return self.audit.listar(modulo=modulo, limit=limit)
