from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from app.models.cliente import Cliente


class ClienteRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id_cliente: int) -> Cliente | None:
        return self.db.query(Cliente).filter(Cliente.id_cliente == id_cliente).first()

    def get_by_documento(self, documento: str) -> Cliente | None:
        return (
            self.db.query(Cliente)
            .filter(func.lower(Cliente.documento) == documento.strip().lower())
            .first()
        )

    def get_by_correo(self, correo: str) -> Cliente | None:
        return (
            self.db.query(Cliente)
            .filter(func.lower(Cliente.correo) == correo.strip().lower())
            .first()
        )

    def listar(self, solo_activos: bool = False, q: str | None = None) -> list[Cliente]:
        query = self.db.query(Cliente)
        if solo_activos:
            query = query.filter(Cliente.activo.is_(True))
        if q:
            patron = f"%{q.strip()}%"
            query = query.filter(or_(Cliente.documento.ilike(patron), Cliente.nombre.ilike(patron)))
        return query.order_by(Cliente.nombre.asc()).all()

    def crear(self, cliente: Cliente) -> Cliente:
        self.db.add(cliente)
        self.db.flush()
        return cliente
