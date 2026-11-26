from sqlalchemy.orm import Session
from app.core.security import hash_password
from app.database.connection import Base, SessionLocal, engine, ensure_mysql_database_exists
import app.models  # noqa: F401 - registra todos los modelos en Base.metadata
from app.models.usuario import Usuario


USUARIOS_SEMILLA = [
    ("Administrador TechStore", "admin@techstore.com", "Admin123*", "ADMINISTRADOR"),
    ("Vendedor TechStore", "vendedor@techstore.com", "Vendedor123*", "VENDEDOR"),
    ("Encargado Inventario", "inventario@techstore.com", "Inventario123*", "ENCARGADO_INVENTARIO"),
]


def seed_default_users(db: Session) -> None:
    if db.query(Usuario).count() > 0:
        return
    for nombre, correo, clave, rol in USUARIOS_SEMILLA:
        db.add(
            Usuario(
                nombre=nombre,
                correo=correo,
                password_hash=hash_password(clave),
                rol=rol,
                activo=True,
            )
        )
    db.commit()


def init_database() -> None:
    ensure_mysql_database_exists()
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_default_users(db)
