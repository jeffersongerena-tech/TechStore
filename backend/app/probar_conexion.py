from sqlalchemy import inspect
from app.core.config import settings
from app.database.connection import engine
from app.database.init_db import init_database


def main() -> None:
    print(f"Conectando a MySQL en {settings.DB_HOST}:{settings.DB_PORT} -> BD '{settings.DB_NAME}'...")
    init_database()
    inspector = inspect(engine)
    tablas = sorted(inspector.get_table_names())
    print(f"Conexión exitosa. Tablas verificadas ({len(tablas)}): {', '.join(tablas)}")


if __name__ == "__main__":
    main()
