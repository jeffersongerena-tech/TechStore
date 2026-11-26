from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.connection import Base
from app.models.types import UInt


class Cliente(Base):
    __tablename__ = "clientes"

    id_cliente: Mapped[int] = mapped_column(UInt, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    documento: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    telefono: Mapped[str | None] = mapped_column(String(30), nullable=True)
    correo: Mapped[str | None] = mapped_column(String(150), unique=True, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    ventas = relationship("Venta", back_populates="cliente")
