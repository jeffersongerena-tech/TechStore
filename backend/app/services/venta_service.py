from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy.orm import Session

from app.core.exceptions import (
    ConflictoNegocioError,
    RecursoNoEncontradoError,
    StockInsuficienteError,
    TechStoreException,
)
from app.models.inventario import MovimientoInventario
from app.models.venta import DetalleVenta, Venta
from app.repositories.auditoria_repo import AuditoriaRepository
from app.repositories.cliente_repo import ClienteRepository
from app.repositories.inventario_repo import InventarioRepository
from app.repositories.producto_repo import ProductoRepository
from app.repositories.venta_repo import VentaRepository
from app.schemas.venta import VentaCreate

CENTAVOS = Decimal("0.01")


class VentaService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = VentaRepository(db)
        self.cli_repo = ClienteRepository(db)
        self.prod_repo = ProductoRepository(db)
        self.inv_repo = InventarioRepository(db)
        self.audit = AuditoriaRepository(db)

    def registrar_venta(self, data: VentaCreate, id_usuario: int) -> Venta:
        """
        Valida existencias disponibles antes de vender, calcula subtotales, descuentos,
        impuestos y total, descuenta stock y registra movimientos (vinculados a id_venta)
        y auditoría dentro de una sola transacción ACID (COMMIT / ROLLBACK).
        """
        try:
            ids_vistos: set[int] = set()
            for item in data.detalles:
                if item.id_producto in ids_vistos:
                    raise ConflictoNegocioError(
                        f"El producto ID {item.id_producto} está repetido en los detalles de la misma venta."
                    )
                ids_vistos.add(item.id_producto)

            cliente = self.cli_repo.get_by_id(data.id_cliente)
            if not cliente:
                raise RecursoNoEncontradoError(f"Cliente con ID {data.id_cliente} no encontrado.")
            if not cliente.activo:
                raise TechStoreException(f"El cliente '{cliente.nombre}' está inactivo.", status_code=400)

            # 1. Bloquear productos y validar stock suficiente antes de realizar descuentos
            productos_bloqueados = {}
            for item in data.detalles:
                prod = self.prod_repo.get_by_id(item.id_producto, for_update=True)
                if not prod:
                    raise RecursoNoEncontradoError(f"Producto con ID {item.id_producto} no existe.")
                if not prod.activo:
                    raise TechStoreException(
                        f"El producto '{prod.codigo} - {prod.nombre}' está desactivado.",
                        status_code=400,
                    )
                if prod.stock_actual < item.cantidad:
                    raise StockInsuficienteError(
                        f"Stock insuficiente para '{prod.codigo} - {prod.nombre}': "
                        f"disponible={prod.stock_actual}, solicitado={item.cantidad}."
                    )
                productos_bloqueados[item.id_producto] = prod

            venta = Venta(
                id_cliente=data.id_cliente,
                id_usuario=id_usuario,
                estado="CONFIRMADA",
            )
            self.repo.crear(venta)

            subtotal_bruto = Decimal("0.00")
            descuento_lineas = Decimal("0.00")

            for item in data.detalles:
                prod = productos_bloqueados[item.id_producto]
                precio_u = (
                    item.precio_unitario
                    if item.precio_unitario is not None
                    else Decimal(str(prod.precio_venta))
                ).quantize(CENTAVOS, rounding=ROUND_HALF_UP)

                bruto_linea = (precio_u * Decimal(item.cantidad)).quantize(CENTAVOS, rounding=ROUND_HALF_UP)
                desc_item = item.descuento.quantize(CENTAVOS, rounding=ROUND_HALF_UP)
                if desc_item > bruto_linea:
                    raise TechStoreException(
                        f"El descuento del producto '{prod.codigo}' (${desc_item}) supera su valor (${bruto_linea}).",
                        status_code=400,
                    )

                subtotal_linea = (bruto_linea - desc_item).quantize(CENTAVOS, rounding=ROUND_HALF_UP)
                subtotal_bruto += bruto_linea
                descuento_lineas += desc_item

                detalle = DetalleVenta(
                    id_venta=venta.id_venta,
                    id_producto=prod.id_producto,
                    cantidad=item.cantidad,
                    precio_unitario=precio_u,
                    descuento=desc_item,
                    subtotal=subtotal_linea,
                )
                self.db.add(detalle)

                prod.stock_actual = prod.stock_actual - item.cantidad

                self.inv_repo.registrar_movimiento(
                    MovimientoInventario(
                        id_producto=prod.id_producto,
                        id_usuario=id_usuario,
                        id_venta=venta.id_venta,
                        tipo="SALIDA",
                        cantidad=item.cantidad,
                        observacion=data.observacion or f"Salida por venta #{venta.id_venta}",
                    )
                )

            descuento_total = (descuento_lineas + data.descuento_adicional).quantize(CENTAVOS, rounding=ROUND_HALF_UP)
            if descuento_total > subtotal_bruto:
                raise TechStoreException(
                    f"El descuento total (${descuento_total}) no puede superar el subtotal (${subtotal_bruto}).",
                    status_code=400,
                )

            base_gravable = subtotal_bruto - descuento_total
            if data.impuesto_fijo is not None:
                impuesto = data.impuesto_fijo.quantize(CENTAVOS, rounding=ROUND_HALF_UP)
            else:
                impuesto = (base_gravable * (data.porcentaje_impuesto / Decimal("100"))).quantize(
                    CENTAVOS, rounding=ROUND_HALF_UP
                )

            venta.subtotal = subtotal_bruto
            venta.descuento = descuento_total
            venta.impuesto = impuesto
            venta.total = (base_gravable + impuesto).quantize(CENTAVOS, rounding=ROUND_HALF_UP)

            self.audit.registrar(
                accion="REGISTRAR_VENTA",
                modulo="VENTAS",
                detalle=f"Venta #{venta.id_venta} registrada por total ${venta.total}",
                id_usuario=id_usuario,
            )

            self.db.commit()
            return self.repo.get_by_id(venta.id_venta)  # type: ignore[return-value]
        except Exception:
            self.db.rollback()
            raise

    def listar_ventas(
        self,
        id_cliente: int | None = None,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
    ) -> list[Venta]:
        return self.repo.listar(
            id_cliente=id_cliente,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
        )

    def consultar_venta(self, id_venta: int) -> Venta:
        venta = self.repo.get_by_id(id_venta)
        if not venta:
            raise RecursoNoEncontradoError(f"Venta con ID {id_venta} no encontrada.")
        return venta
