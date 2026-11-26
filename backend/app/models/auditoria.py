from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.connection import Base
from app.models.types import UBigInt, UInt


class Auditoria(Base):
    __tablename__ = "auditoria"

    id_auditoria: Mapped[int] = mapped_column(UBigInt, primary_key=True, autoincrement=True)
    id_usuario: Mapped[int | None] = mapped_column(
        UInt, ForeignKey("usuarios.id_usuario", onupdate="CASCADE", ondelete="SET NULL"), nullable=True, index=True
    )
    accion: Mapped[str] = mapped_column(String(50), nullable=False)
    modulo: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    detalle: Mapped[str | None] = mapped_column(String(500), nullable=True)
    fecha: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), index=True)

    usuario = relationship("Usuario", back_populates="auditorias")
