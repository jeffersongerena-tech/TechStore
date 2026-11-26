from datetime import datetime
from decimal import Decimal
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.connection import Base
from app.models.types import UBigInt, UInt


class Venta(Base):
    __tablename__ = "ventas"
    __table_args__ = (
        CheckConstraint("subtotal >= 0", name="chk_venta_subtotal"),
        CheckConstraint("descuento >= 0", name="chk_venta_descuento"),
        CheckConstraint("impuesto >= 0", name="chk_venta_impuesto"),
        CheckConstraint("total >= 0", name="chk_venta_total"),
    )

    id_venta: Mapped[int] = mapped_column(UBigInt, primary_key=True, autoincrement=True)
    id_cliente: Mapped[int] = mapped_column(
        UInt, ForeignKey("clientes.id_cliente", onupdate="CASCADE"), nullable=False, index=True
    )
    id_usuario: Mapped[int] = mapped_column(
        UInt, ForeignKey("usuarios.id_usuario", onupdate="CASCADE"), nullable=False, index=True
    )
    fecha: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), index=True)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    descuento: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    impuesto: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    total: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="CONFIRMADA")

    cliente = relationship("Cliente", back_populates="ventas")
    usuario = relationship("Usuario", back_populates="ventas")
    detalles = relationship("DetalleVenta", back_populates="venta", cascade="all, delete-orphan")
    movimientos = relationship("MovimientoInventario", back_populates="venta")


class DetalleVenta(Base):
    __tablename__ = "detalle_ventas"
    __table_args__ = (
        UniqueConstraint("id_venta", "id_producto", name="uq_detalle_ventas_producto"),
        CheckConstraint("cantidad > 0", name="chk_det_venta_cant"),
        CheckConstraint("precio_unitario >= 0", name="chk_det_venta_precio"),
        CheckConstraint("descuento >= 0", name="chk_det_venta_desc"),
    )

    id_detalle_venta: Mapped[int] = mapped_column(UBigInt, primary_key=True, autoincrement=True)
    id_venta: Mapped[int] = mapped_column(
        UBigInt, ForeignKey("ventas.id_venta", onupdate="CASCADE"), nullable=False, index=True
    )
    id_producto: Mapped[int] = mapped_column(
        UInt, ForeignKey("productos.id_producto", onupdate="CASCADE"), nullable=False, index=True
    )
    cantidad: Mapped[int] = mapped_column(UInt, nullable=False)
    precio_unitario: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    descuento: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    subtotal: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    venta = relationship("Venta", back_populates="detalles")
    producto = relationship("Producto", back_populates="detalles_venta")
