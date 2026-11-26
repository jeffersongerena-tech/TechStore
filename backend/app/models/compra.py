from datetime import datetime
from decimal import Decimal
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.connection import Base
from app.models.types import UBigInt, UInt


class Compra(Base):
    __tablename__ = "compras"
    __table_args__ = (CheckConstraint("total >= 0", name="chk_compra_total"),)

    id_compra: Mapped[int] = mapped_column(UBigInt, primary_key=True, autoincrement=True)
    id_proveedor: Mapped[int] = mapped_column(
        UInt, ForeignKey("proveedores.id_proveedor", onupdate="CASCADE"), nullable=False, index=True
    )
    id_usuario: Mapped[int] = mapped_column(
        UInt, ForeignKey("usuarios.id_usuario", onupdate="CASCADE"), nullable=False, index=True
    )
    fecha: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), index=True)
    total: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="CONFIRMADA")

    proveedor = relationship("Proveedor", back_populates="compras")
    usuario = relationship("Usuario", back_populates="compras")
    detalles = relationship("DetalleCompra", back_populates="compra", cascade="all, delete-orphan")
    movimientos = relationship("MovimientoInventario", back_populates="compra")


class DetalleCompra(Base):
    __tablename__ = "detalle_compras"
    __table_args__ = (
        UniqueConstraint("id_compra", "id_producto", name="uq_detalle_compras_producto"),
        CheckConstraint("cantidad > 0", name="chk_det_compra_cant"),
        CheckConstraint("costo_unitario >= 0", name="chk_det_compra_costo"),
    )

    id_detalle_compra: Mapped[int] = mapped_column(UBigInt, primary_key=True, autoincrement=True)
    id_compra: Mapped[int] = mapped_column(
        UBigInt, ForeignKey("compras.id_compra", onupdate="CASCADE"), nullable=False, index=True
    )
    id_producto: Mapped[int] = mapped_column(
        UInt, ForeignKey("productos.id_producto", onupdate="CASCADE"), nullable=False, index=True
    )
    cantidad: Mapped[int] = mapped_column(UInt, nullable=False)
    costo_unitario: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    compra = relationship("Compra", back_populates="detalles")
    producto = relationship("Producto", back_populates="detalles_compra")
