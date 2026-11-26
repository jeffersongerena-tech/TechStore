from sqlalchemy.orm import Session
from app.core.exceptions import ConflictoNegocioError, RecursoNoEncontradoError
from app.models.cliente import Cliente
from app.models.proveedor import Proveedor
from app.repositories.auditoria_repo import AuditoriaRepository
from app.repositories.cliente_repo import ClienteRepository
from app.repositories.proveedor_repo import ProveedorRepository
from app.schemas.terceros import ClienteCreate, ClienteUpdate, ProveedorCreate, ProveedorUpdate


class ProveedorService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ProveedorRepository(db)
        self.audit = AuditoriaRepository(db)

    def registrar(self, data: ProveedorCreate, id_usuario: int | None = None) -> Proveedor:
        if self.repo.get_by_documento(data.documento):
            raise ConflictoNegocioError(f"Ya existe un proveedor con el documento/NIT '{data.documento}'.")
        if data.correo and self.repo.get_by_correo(data.correo):
            raise ConflictoNegocioError(f"Ya existe un proveedor con el correo '{data.correo}'.")
        try:
            prov = Proveedor(**data.model_dump(), activo=True)
            self.repo.crear(prov)
            self.audit.registrar(
                accion="CREAR_PROVEEDOR",
                modulo="PROVEEDORES",
                detalle=f"Proveedor '{prov.nombre}' (Doc {prov.documento}) registrado",
                id_usuario=id_usuario,
            )
            self.db.commit()
            self.db.refresh(prov)
            return prov
        except Exception:
            self.db.rollback()
            raise

    def listar(self, solo_activos: bool = False, q: str | None = None) -> list[Proveedor]:
        return self.repo.listar(solo_activos=solo_activos, q=q)

    def consultar(self, id_proveedor: int) -> Proveedor:
        prov = self.repo.get_by_id(id_proveedor)
        if not prov:
            raise RecursoNoEncontradoError(f"Proveedor con ID {id_proveedor} no encontrado.")
        return prov

    def actualizar(self, id_proveedor: int, data: ProveedorUpdate, id_usuario: int | None = None) -> Proveedor:
        prov = self.consultar(id_proveedor)
        if data.documento and data.documento.lower() != prov.documento.lower():
            dup = self.repo.get_by_documento(data.documento)
            if dup and dup.id_proveedor != id_proveedor:
                raise ConflictoNegocioError(f"Ya existe otro proveedor con el documento '{data.documento}'.")
        if data.correo and (not prov.correo or data.correo.lower() != prov.correo.lower()):
            dup_c = self.repo.get_by_correo(data.correo)
            if dup_c and dup_c.id_proveedor != id_proveedor:
                raise ConflictoNegocioError(f"Ya existe otro proveedor con el correo '{data.correo}'.")
        try:
            for campo, valor in data.model_dump(exclude_unset=True).items():
                setattr(prov, campo, valor)
            self.audit.registrar(
                accion="ACTUALIZAR_PROVEEDOR",
                modulo="PROVEEDORES",
                detalle=f"Proveedor ID {id_proveedor} ('{prov.nombre}') actualizado",
                id_usuario=id_usuario,
            )
            self.db.commit()
            self.db.refresh(prov)
            return prov
        except Exception:
            self.db.rollback()
            raise


class ClienteService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ClienteRepository(db)
        self.audit = AuditoriaRepository(db)

    def registrar(self, data: ClienteCreate, id_usuario: int | None = None) -> Cliente:
        if self.repo.get_by_documento(data.documento):
            raise ConflictoNegocioError(f"Ya existe un cliente con el documento '{data.documento}'.")
        if data.correo and self.repo.get_by_correo(data.correo):
            raise ConflictoNegocioError(f"Ya existe un cliente con el correo '{data.correo}'.")
        try:
            cli = Cliente(**data.model_dump(), activo=True)
            self.repo.crear(cli)
            self.audit.registrar(
                accion="CREAR_CLIENTE",
                modulo="CLIENTES",
                detalle=f"Cliente '{cli.nombre}' (Doc {cli.documento}) registrado",
                id_usuario=id_usuario,
            )
            self.db.commit()
            self.db.refresh(cli)
            return cli
        except Exception:
            self.db.rollback()
            raise

    def listar(self, solo_activos: bool = False, q: str | None = None) -> list[Cliente]:
        return self.repo.listar(solo_activos=solo_activos, q=q)

    def consultar(self, id_cliente: int) -> Cliente:
        cli = self.repo.get_by_id(id_cliente)
        if not cli:
            raise RecursoNoEncontradoError(f"Cliente con ID {id_cliente} no encontrado.")
        return cli

    def actualizar(self, id_cliente: int, data: ClienteUpdate, id_usuario: int | None = None) -> Cliente:
        cli = self.consultar(id_cliente)
        if data.documento and data.documento.lower() != cli.documento.lower():
            dup = self.repo.get_by_documento(data.documento)
            if dup and dup.id_cliente != id_cliente:
                raise ConflictoNegocioError(f"Ya existe otro cliente con el documento '{data.documento}'.")
        if data.correo and (not cli.correo or data.correo.lower() != cli.correo.lower()):
            dup_c = self.repo.get_by_correo(data.correo)
            if dup_c and dup_c.id_cliente != id_cliente:
                raise ConflictoNegocioError(f"Ya existe otro cliente con el correo '{data.correo}'.")
        try:
            for campo, valor in data.model_dump(exclude_unset=True).items():
                setattr(cli, campo, valor)
            self.audit.registrar(
                accion="ACTUALIZAR_CLIENTE",
                modulo="CLIENTES",
                detalle=f"Cliente ID {id_cliente} ('{cli.nombre}') actualizado",
                id_usuario=id_usuario,
            )
            self.db.commit()
            self.db.refresh(cli)
            return cli
        except Exception:
            self.db.rollback()
            raise
