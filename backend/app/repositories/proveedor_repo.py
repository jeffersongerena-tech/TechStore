from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from app.models.proveedor import Proveedor


class ProveedorRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id_proveedor: int) -> Proveedor | None:
        return self.db.query(Proveedor).filter(Proveedor.id_proveedor == id_proveedor).first()

    def get_by_documento(self, documento: str) -> Proveedor | None:
        return (
            self.db.query(Proveedor)
            .filter(func.lower(Proveedor.documento) == documento.strip().lower())
            .first()
        )

    def get_by_correo(self, correo: str) -> Proveedor | None:
        return (
            self.db.query(Proveedor)
            .filter(func.lower(Proveedor.correo) == correo.strip().lower())
            .first()
        )

    def listar(self, solo_activos: bool = False, q: str | None = None) -> list[Proveedor]:
        query = self.db.query(Proveedor)
        if solo_activos:
            query = query.filter(Proveedor.activo.is_(True))
        if q:
            patron = f"%{q.strip()}%"
            query = query.filter(or_(Proveedor.documento.ilike(patron), Proveedor.nombre.ilike(patron)))
        return query.order_by(Proveedor.nombre.asc()).all()

    def crear(self, proveedor: Proveedor) -> Proveedor:
        self.db.add(proveedor)
        self.db.flush()
        return proveedor
