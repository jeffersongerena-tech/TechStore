from datetime import datetime
from decimal import Decimal
from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.connection import Base
from app.models.types import UInt


class Producto(Base):
    __tablename__ = "productos"
    __table_args__ = (
        CheckConstraint("costo_actual >= 0", name="chk_prod_costo"),
        CheckConstraint("precio_venta >= 0", name="chk_prod_precio"),
        CheckConstraint("stock_actual >= 0", name="chk_prod_stock"),
        CheckConstraint("stock_minimo >= 0", name="chk_prod_stock_min"),
    )

    id_producto: Mapped[int] = mapped_column(UInt, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String(255), nullable=True)
    id_categoria: Mapped[int] = mapped_column(
        UInt, ForeignKey("categorias.id_categoria", onupdate="CASCADE"), nullable=False, index=True
    )
    precio_venta: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    costo_actual: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    stock_actual: Mapped[int] = mapped_column(UInt, nullable=False, default=0)
    stock_minimo: Mapped[int] = mapped_column(UInt, nullable=False, default=0)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    categoria = relationship("Categoria", back_populates="productos")
    detalles_compra = relationship("DetalleCompra", back_populates="producto")
    detalles_venta = relationship("DetalleVenta", back_populates="producto")
    movimientos = relationship("MovimientoInventario", back_populates="producto")

    @property
    def stock_bajo(self) -> bool:
        return self.stock_actual <= self.stock_minimo
