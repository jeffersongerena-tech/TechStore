from datetime import date
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from app.models.compra import Compra


class CompraRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id_compra: int) -> Compra | None:
        return (
            self.db.query(Compra)
            .options(joinedload(Compra.detalles))
            .filter(Compra.id_compra == id_compra)
            .first()
        )

    def listar(
        self,
        id_proveedor: int | None = None,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
    ) -> list[Compra]:
        query = self.db.query(Compra).options(joinedload(Compra.detalles))
        if id_proveedor is not None:
            query = query.filter(Compra.id_proveedor == id_proveedor)
        if fecha_desde is not None:
            query = query.filter(func.date(Compra.fecha) >= fecha_desde)
        if fecha_hasta is not None:
            query = query.filter(func.date(Compra.fecha) <= fecha_hasta)
        return query.order_by(Compra.id_compra.desc()).all()

    def crear(self, compra: Compra) -> Compra:
        self.db.add(compra)
        self.db.flush()
        return compra
