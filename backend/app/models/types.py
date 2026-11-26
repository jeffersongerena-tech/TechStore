from sqlalchemy import Integer
from sqlalchemy.dialects.mysql import BIGINT, INTEGER

# Exactamente igual a techstore_db.sql en MariaDB/MySQL (INT UNSIGNED / BIGINT UNSIGNED)
# y compatible con SQLite en memoria para las pruebas automatizadas.
UInt = INTEGER(unsigned=True).with_variant(Integer(), "sqlite")
UBigInt = BIGINT(unsigned=True).with_variant(Integer(), "sqlite")
