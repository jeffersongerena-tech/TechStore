from datetime import datetime
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.connection import Base
from app.models.types import UBigInt, UInt


class MovimientoInventario(Base):
    __tablename__ = "movimientos_inventario"
    __table_args__ = (CheckConstraint("cantidad > 0", name="chk_mov_cant"),)

    id_movimiento: Mapped[int] = mapped_column(UBigInt, primary_key=True, autoincrement=True)
    id_producto: Mapped[int] = mapped_column(
        UInt, ForeignKey("productos.id_producto", onupdate="CASCADE"), nullable=False, index=True
    )
    id_usuario: Mapped[int | None] = mapped_column(
        UInt, ForeignKey("usuarios.id_usuario", onupdate="CASCADE", ondelete="SET NULL"), nullable=True, index=True
    )
    id_compra: Mapped[int | None] = mapped_column(
        UBigInt, ForeignKey("compras.id_compra", onupdate="CASCADE"), nullable=True, index=True
    )
    id_venta: Mapped[int | None] = mapped_column(
        UBigInt, ForeignKey("ventas.id_venta", onupdate="CASCADE"), nullable=True, index=True
    )
    tipo: Mapped[str] = mapped_column(String(10), nullable=False)  # ENTRADA | SALIDA
    cantidad: Mapped[int] = mapped_column(UInt, nullable=False)
    fecha: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), index=True)
    observacion: Mapped[str | None] = mapped_column(String(255), nullable=True)

    producto = relationship("Producto", back_populates="movimientos")
    usuario = relationship("Usuario", back_populates="movimientos")
    compra = relationship("Compra", back_populates="movimientos")
    venta = relationship("Venta", back_populates="movimientos")
