from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.categoria import Categoria


class CategoriaRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id_categoria: int) -> Categoria | None:
        return self.db.query(Categoria).filter(Categoria.id_categoria == id_categoria).first()

    def get_by_nombre(self, nombre: str) -> Categoria | None:
        return (
            self.db.query(Categoria)
            .filter(func.lower(Categoria.nombre) == nombre.strip().lower())
            .first()
        )

    def listar(self, solo_activas: bool = False, q: str | None = None) -> list[Categoria]:
        query = self.db.query(Categoria)
        if solo_activas:
            query = query.filter(Categoria.activa.is_(True))
        if q:
            query = query.filter(Categoria.nombre.ilike(f"%{q.strip()}%"))
        return query.order_by(Categoria.nombre.asc()).all()

    def crear(self, categoria: Categoria) -> Categoria:
        self.db.add(categoria)
        self.db.flush()
        return categoria
