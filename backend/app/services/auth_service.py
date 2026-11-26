from sqlalchemy.orm import Session
from app.core.exceptions import ConflictoNegocioError, RecursoNoEncontradoError, TechStoreException
from app.core.security import create_access_token, hash_password, verify_password
from app.models.usuario import Usuario
from app.repositories.auditoria_repo import AuditoriaRepository
from app.repositories.usuario_repo import UsuarioRepository
from app.schemas.usuario import LoginRequest, TokenResponse, UsuarioCreate, UsuarioOut, UsuarioUpdate


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = UsuarioRepository(db)
        self.audit = AuditoriaRepository(db)

    def login(self, data: LoginRequest) -> TokenResponse:
        usuario = self.repo.get_by_correo(data.correo)
        if not usuario or not verify_password(data.password, usuario.password_hash):
            raise TechStoreException("Credenciales inválidas (correo o contraseña incorrectos).", status_code=401)
        if not usuario.activo:
            raise TechStoreException("La cuenta de usuario se encuentra desactivada.", status_code=403)

        try:
            self.audit.registrar(
                accion="INICIO_SESION",
                modulo="AUTENTICACION",
                detalle=f"Inicio de sesión exitoso de {usuario.correo} ({usuario.rol})",
                id_usuario=usuario.id_usuario,
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

        token = create_access_token(subject=str(usuario.id_usuario), rol=usuario.rol)
        return TokenResponse(access_token=token, usuario=UsuarioOut.model_validate(usuario))

    def crear_usuario(self, data: UsuarioCreate, id_actor: int | None = None) -> Usuario:
        if self.repo.get_by_correo(data.correo):
            raise ConflictoNegocioError(f"Ya existe un usuario registrado con el correo '{data.correo}'.")
        try:
            nuevo = Usuario(
                nombre=data.nombre,
                correo=data.correo.lower(),
                password_hash=hash_password(data.password),
                rol=data.rol,
                activo=True,
            )
            self.repo.crear(nuevo)
            self.audit.registrar(
                accion="CREAR_USUARIO",
                modulo="USUARIOS",
                detalle=f"Usuario '{nuevo.correo}' creado con rol {nuevo.rol}",
                id_usuario=id_actor,
            )
            self.db.commit()
            self.db.refresh(nuevo)
            return nuevo
        except Exception:
            self.db.rollback()
            raise

    def listar_usuarios(self) -> list[Usuario]:
        return self.repo.listar()

    def actualizar_usuario(self, id_usuario: int, data: UsuarioUpdate, id_actor: int | None = None) -> Usuario:
        usuario = self.repo.get_by_id(id_usuario)
        if not usuario:
            raise RecursoNoEncontradoError(f"Usuario con ID {id_usuario} no encontrado.")
        try:
            cambios = data.model_dump(exclude_unset=True)
            for campo, valor in cambios.items():
                setattr(usuario, campo, valor)
            self.audit.registrar(
                accion="ACTUALIZAR_USUARIO",
                modulo="USUARIOS",
                detalle=f"Usuario ID {id_usuario} actualizado: {cambios}",
                id_usuario=id_actor,
            )
            self.db.commit()
            self.db.refresh(usuario)
            return usuario
        except Exception:
            self.db.rollback()
            raise
