from datetime import date
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from app.models.venta import Venta


class VentaRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id_venta: int) -> Venta | None:
        return (
            self.db.query(Venta)
            .options(joinedload(Venta.detalles))
            .filter(Venta.id_venta == id_venta)
            .first()
        )

    def listar(
        self,
        id_cliente: int | None = None,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
    ) -> list[Venta]:
        query = self.db.query(Venta).options(joinedload(Venta.detalles))
        if id_cliente is not None:
            query = query.filter(Venta.id_cliente == id_cliente)
        if fecha_desde is not None:
            query = query.filter(func.date(Venta.fecha) >= fecha_desde)
        if fecha_hasta is not None:
            query = query.filter(func.date(Venta.fecha) <= fecha_hasta)
        return query.order_by(Venta.id_venta.desc()).all()

    def crear(self, venta: Venta) -> Venta:
        self.db.add(venta)
        self.db.flush()
        return venta
