from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from app.models.producto import Producto


class ProductoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id_producto: int, for_update: bool = False) -> Producto | None:
        q = self.db.query(Producto).filter(Producto.id_producto == id_producto)
        if for_update:
            q = q.with_for_update()
        return q.first()

    def get_by_codigo(self, codigo: str) -> Producto | None:
        return (
            self.db.query(Producto)
            .filter(func.lower(Producto.codigo) == codigo.strip().lower())
            .first()
        )

    def listar(
        self,
        id_categoria: int | None = None,
        solo_activos: bool = False,
        q: str | None = None,
    ) -> list[Producto]:
        query = self.db.query(Producto)
        if id_categoria is not None:
            query = query.filter(Producto.id_categoria == id_categoria)
        if solo_activos:
            query = query.filter(Producto.activo.is_(True))
        if q:
            patron = f"%{q.strip()}%"
            query = query.filter(or_(Producto.codigo.ilike(patron), Producto.nombre.ilike(patron)))
        return query.order_by(Producto.nombre.asc()).all()

    def listar_stock_bajo(self) -> list[Producto]:
        return (
            self.db.query(Producto)
            .filter(Producto.activo.is_(True), Producto.stock_actual <= Producto.stock_minimo)
            .order_by(Producto.stock_actual.asc())
            .all()
        )

    def crear(self, producto: Producto) -> Producto:
        self.db.add(producto)
        self.db.flush()
        return producto
