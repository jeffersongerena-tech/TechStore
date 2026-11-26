from sqlalchemy.orm import Session
from app.models.inventario import MovimientoInventario


class InventarioRepository:
    def __init__(self, db: Session):
        self.db = db

    def registrar_movimiento(self, mov: MovimientoInventario) -> MovimientoInventario:
        self.db.add(mov)
        self.db.flush()
        return mov

    def listar(
        self,
        id_producto: int | None = None,
        tipo: str | None = None,
        limit: int = 200,
    ) -> list[MovimientoInventario]:
        q = self.db.query(MovimientoInventario)
        if id_producto is not None:
            q = q.filter(MovimientoInventario.id_producto == id_producto)
        if tipo:
            q = q.filter(MovimientoInventario.tipo == tipo.upper())
        return q.order_by(MovimientoInventario.id_movimiento.desc()).limit(limit).all()
