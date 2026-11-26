from sqlalchemy.orm import Session
from app.core.exceptions import ConflictoNegocioError, RecursoNoEncontradoError
from app.models.categoria import Categoria
from app.repositories.auditoria_repo import AuditoriaRepository
from app.repositories.categoria_repo import CategoriaRepository
from app.schemas.categoria import CategoriaCreate, CategoriaUpdate


class CategoriaService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = CategoriaRepository(db)
        self.audit = AuditoriaRepository(db)

    def registrar(self, data: CategoriaCreate, id_usuario: int | None = None) -> Categoria:
        if self.repo.get_by_nombre(data.nombre):
            raise ConflictoNegocioError(f"Ya existe una categoría con el nombre '{data.nombre}'.")
        try:
            categoria = Categoria(nombre=data.nombre, descripcion=data.descripcion, activa=True)
            self.repo.crear(categoria)
            self.audit.registrar(
                accion="CREAR_CATEGORIA",
                modulo="CATEGORIAS",
                detalle=f"Categoría '{categoria.nombre}' registrada (ID {categoria.id_categoria})",
                id_usuario=id_usuario,
            )
            self.db.commit()
            self.db.refresh(categoria)
            return categoria
        except Exception:
            self.db.rollback()
            raise

    def listar(self, solo_activas: bool = False, q: str | None = None) -> list[Categoria]:
        return self.repo.listar(solo_activas=solo_activas, q=q)

    def consultar(self, id_categoria: int) -> Categoria:
        categoria = self.repo.get_by_id(id_categoria)
        if not categoria:
            raise RecursoNoEncontradoError(f"Categoría con ID {id_categoria} no encontrada.")
        return categoria

    def actualizar(self, id_categoria: int, data: CategoriaUpdate, id_usuario: int | None = None) -> Categoria:
        categoria = self.consultar(id_categoria)
        if data.nombre and data.nombre.lower() != categoria.nombre.lower():
            existente = self.repo.get_by_nombre(data.nombre)
            if existente and existente.id_categoria != id_categoria:
                raise ConflictoNegocioError(f"Ya existe otra categoría con el nombre '{data.nombre}'.")
        try:
            for campo, valor in data.model_dump(exclude_unset=True).items():
                setattr(categoria, campo, valor)
            self.audit.registrar(
                accion="ACTUALIZAR_CATEGORIA",
                modulo="CATEGORIAS",
                detalle=f"Categoría ID {id_categoria} ('{categoria.nombre}') actualizada",
                id_usuario=id_usuario,
            )
            self.db.commit()
            self.db.refresh(categoria)
            return categoria
        except Exception:
            self.db.rollback()
            raise

    def desactivar(self, id_categoria: int, id_usuario: int | None = None) -> Categoria:
        categoria = self.consultar(id_categoria)
        try:
            categoria.activa = False
            self.audit.registrar(
                accion="DESACTIVAR_CATEGORIA",
                modulo="CATEGORIAS",
                detalle=f"Categoría ID {id_categoria} ('{categoria.nombre}') desactivada",
                id_usuario=id_usuario,
            )
            self.db.commit()
            self.db.refresh(categoria)
            return categoria
        except Exception:
            self.db.rollback()
            raise
