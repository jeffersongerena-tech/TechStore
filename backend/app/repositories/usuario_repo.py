from sqlalchemy.orm import Session
from app.models.usuario import Usuario


class UsuarioRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id_usuario: int) -> Usuario | None:
        return self.db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()

    def get_by_correo(self, correo: str) -> Usuario | None:
        return self.db.query(Usuario).filter(Usuario.correo == correo.lower()).first()

    def listar(self) -> list[Usuario]:
        return self.db.query(Usuario).order_by(Usuario.id_usuario.asc()).all()

    def crear(self, usuario: Usuario) -> Usuario:
        self.db.add(usuario)
        self.db.flush()
        return usuario
