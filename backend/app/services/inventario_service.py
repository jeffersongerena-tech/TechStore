from sqlalchemy.orm import Session

from app.core.exceptions import RecursoNoEncontradoError, StockInsuficienteError, TechStoreException
from app.models.inventario import MovimientoInventario
from app.repositories.auditoria_repo import AuditoriaRepository
from app.repositories.inventario_repo import InventarioRepository
from app.repositories.producto_repo import ProductoRepository
from app.schemas.inventario import AlertaStockOut, MovimientoCreate


class InventarioService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = InventarioRepository(db)
        self.prod_repo = ProductoRepository(db)
        self.audit = AuditoriaRepository(db)

    def registrar_ajuste(self, data: MovimientoCreate, id_usuario: int) -> MovimientoInventario:
        try:
            producto = self.prod_repo.get_by_id(data.id_producto, for_update=True)
            if not producto:
                raise RecursoNoEncontradoError(f"Producto con ID {data.id_producto} no encontrado.")
            if not producto.activo:
                raise TechStoreException(
                    f"El producto '{producto.codigo} - {producto.nombre}' está desactivado.",
                    status_code=400,
                )

            stock_anterior = producto.stock_actual
            if data.tipo == "ENTRADA":
                nuevo_stock = stock_anterior + data.cantidad
            else:
                if stock_anterior < data.cantidad:
                    raise StockInsuficienteError(
                        f"No se puede registrar salida de {data.cantidad} unidades para '{producto.codigo}': "
                        f"stock actual={stock_anterior}."
                    )
                nuevo_stock = stock_anterior - data.cantidad

            producto.stock_actual = nuevo_stock

            mov = MovimientoInventario(
                id_producto=producto.id_producto,
                id_usuario=id_usuario,
                tipo=data.tipo,
                cantidad=data.cantidad,
                observacion=data.observacion,
            )
            self.repo.registrar_movimiento(mov)

            self.audit.registrar(
                accion=f"MOVIMIENTO_{data.tipo}",
                modulo="INVENTARIO",
                detalle=(
                    f"{data.tipo} de {data.cantidad} uds en '{producto.codigo}' "
                    f"({stock_anterior} -> {nuevo_stock}). Obs: {data.observacion}"
                ),
                id_usuario=id_usuario,
            )

            self.db.commit()
            self.db.refresh(mov)
            return mov
        except Exception:
            self.db.rollback()
            raise

    def listar_movimientos(
        self,
        id_producto: int | None = None,
        tipo: str | None = None,
    ) -> list[MovimientoInventario]:
        return self.repo.listar(id_producto=id_producto, tipo=tipo)

    def consultar_alertas_stock_bajo(self) -> list[AlertaStockOut]:
        productos = self.prod_repo.listar_stock_bajo()
        return [
            AlertaStockOut(
                id_producto=p.id_producto,
                codigo=p.codigo,
                nombre=p.nombre,
                stock_actual=p.stock_actual,
                stock_minimo=p.stock_minimo,
                deficit=max(0, p.stock_minimo - p.stock_actual),
            )
            for p in productos
        ]
