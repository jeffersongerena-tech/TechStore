from sqlalchemy.orm import Session
from app.models.auditoria import Auditoria


class AuditoriaRepository:
    def __init__(self, db: Session):
        self.db = db

    def registrar(self, accion: str, modulo: str, detalle: str | None, id_usuario: int | None) -> Auditoria:
        item = Auditoria(
            accion=accion,
            modulo=modulo,
            detalle=detalle,
            id_usuario=id_usuario,
        )
        self.db.add(item)
        self.db.flush()
        return item

    def listar(self, modulo: str | None = None, limit: int = 100) -> list[Auditoria]:
        q = self.db.query(Auditoria)
        if modulo:
            q = q.filter(Auditoria.modulo == modulo.upper())
        return q.order_by(Auditoria.id_auditoria.desc()).limit(limit).all()
