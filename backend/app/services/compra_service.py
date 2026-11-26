from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictoNegocioError, RecursoNoEncontradoError, TechStoreException
from app.models.compra import Compra, DetalleCompra
from app.models.inventario import MovimientoInventario
from app.repositories.auditoria_repo import AuditoriaRepository
from app.repositories.compra_repo import CompraRepository
from app.repositories.inventario_repo import InventarioRepository
from app.repositories.producto_repo import ProductoRepository
from app.repositories.proveedor_repo import ProveedorRepository
from app.schemas.compra import CompraCreate

CENTAVOS = Decimal("0.01")


class CompraService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = CompraRepository(db)
        self.prov_repo = ProveedorRepository(db)
        self.prod_repo = ProductoRepository(db)
        self.inv_repo = InventarioRepository(db)
        self.audit = AuditoriaRepository(db)

    def registrar_compra(self, data: CompraCreate, id_usuario: int) -> Compra:
        """
        Registra encabezado y detalles de compra, calcula totales, incrementa el stock
        de cada producto, genera movimientos de inventario (vinculados a id_compra) y
        auditoría en una sola transacción ACID (COMMIT / ROLLBACK).
        """
        try:
            # Validar que no se repita el mismo producto en dos líneas (uq_detalle_compras_producto)
            ids_vistos: set[int] = set()
            for item in data.detalles:
                if item.id_producto in ids_vistos:
                    raise ConflictoNegocioError(
                        f"El producto ID {item.id_producto} está repetido en los detalles de la misma compra."
                    )
                ids_vistos.add(item.id_producto)

            proveedor = self.prov_repo.get_by_id(data.id_proveedor)
            if not proveedor:
                raise RecursoNoEncontradoError(f"Proveedor con ID {data.id_proveedor} no encontrado.")
            if not proveedor.activo:
                raise TechStoreException(f"El proveedor '{proveedor.nombre}' está inactivo.", status_code=400)

            compra = Compra(
                id_proveedor=data.id_proveedor,
                id_usuario=id_usuario,
                total=Decimal("0.00"),
                estado="CONFIRMADA",
            )
            self.repo.crear(compra)

            total_compra = Decimal("0.00")

            for item in data.detalles:
                producto = self.prod_repo.get_by_id(item.id_producto, for_update=True)
                if not producto:
                    raise RecursoNoEncontradoError(f"Producto con ID {item.id_producto} no existe.")
                if not producto.activo:
                    raise TechStoreException(
                        f"El producto '{producto.codigo} - {producto.nombre}' está desactivado.",
                        status_code=400,
                    )

                costo_u = item.costo_unitario.quantize(CENTAVOS, rounding=ROUND_HALF_UP)
                subtotal = (costo_u * Decimal(item.cantidad)).quantize(CENTAVOS, rounding=ROUND_HALF_UP)
                total_compra += subtotal

                detalle = DetalleCompra(
                    id_compra=compra.id_compra,
                    id_producto=producto.id_producto,
                    cantidad=item.cantidad,
                    costo_unitario=costo_u,
                    subtotal=subtotal,
                )
                self.db.add(detalle)

                producto.stock_actual = producto.stock_actual + item.cantidad
                producto.costo_actual = costo_u

                self.inv_repo.registrar_movimiento(
                    MovimientoInventario(
                        id_producto=producto.id_producto,
                        id_usuario=id_usuario,
                        id_compra=compra.id_compra,
                        tipo="ENTRADA",
                        cantidad=item.cantidad,
                        observacion=data.observacion or f"Entrada por compra #{compra.id_compra}",
                    )
                )

            compra.total = total_compra.quantize(CENTAVOS, rounding=ROUND_HALF_UP)

            self.audit.registrar(
                accion="REGISTRAR_COMPRA",
                modulo="COMPRAS",
                detalle=f"Compra #{compra.id_compra} registrada por total ${compra.total}",
                id_usuario=id_usuario,
            )

            self.db.commit()
            return self.repo.get_by_id(compra.id_compra)  # type: ignore[return-value]
        except Exception:
            self.db.rollback()
            raise

    def listar_compras(
        self,
        id_proveedor: int | None = None,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
    ) -> list[Compra]:
        return self.repo.listar(
            id_proveedor=id_proveedor,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
        )

    def consultar_compra(self, id_compra: int) -> Compra:
        compra = self.repo.get_by_id(id_compra)
        if not compra:
            raise RecursoNoEncontradoError(f"Compra con ID {id_compra} no encontrada.")
        return compra
