import os
import unittest
from decimal import Decimal

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["REQUIRE_AUTH"] = "false"

from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.exceptions import ConflictoNegocioError, StockInsuficienteError
from app.database.connection import Base
from app.database.init_db import seed_default_users
from app.models.producto import Producto
from app.models.usuario import Usuario
from app.schemas.categoria import CategoriaCreate, CategoriaUpdate
from app.schemas.compra import CompraCreate, DetalleCompraIn
from app.schemas.inventario import MovimientoCreate
from app.schemas.producto import ProductoCreate
from app.schemas.terceros import ClienteCreate, ProveedorCreate
from app.schemas.venta import DetalleVentaIn, VentaCreate
from app.services.categoria_service import CategoriaService
from app.services.compra_service import CompraService
from app.services.inventario_service import InventarioService
from app.services.producto_service import ProductoService
from app.services.reporte_service import ReporteService
from app.services.terceros_service import ClienteService, ProveedorService
from app.services.venta_service import VentaService


class TestServiciosTechStore(unittest.TestCase):
    """Pruebas automatizadas sincronizadas con techstore_db.sql (Actividad 4)."""

    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        self.Session = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        self.db = self.Session()
        seed_default_users(self.db)
        self.admin = self.db.query(Usuario).filter(Usuario.rol == "ADMINISTRADOR").first()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_01_categorias_registrar_listar_consultar_actualizar_desactivar(self):
        srv = CategoriaService(self.db)
        cat = srv.registrar(CategoriaCreate(nombre="Portátiles", descripcion="Equipos portátiles"), self.admin.id_usuario)
        self.assertTrue(cat.activa)

        with self.assertRaises(ConflictoNegocioError):
            srv.registrar(CategoriaCreate(nombre="portátiles"), self.admin.id_usuario)

        actualizada = srv.actualizar(cat.id_categoria, CategoriaUpdate(nombre="Laptops Pro"), self.admin.id_usuario)
        self.assertEqual(actualizada.nombre, "Laptops Pro")

        desactivada = srv.desactivar(cat.id_categoria, self.admin.id_usuario)
        self.assertFalse(desactivada.activa)
        self.assertEqual(len(srv.listar(solo_activas=True)), 0)

    def test_02_productos_validaciones_codigo_unico_precios_y_existencias(self):
        cat = CategoriaService(self.db).registrar(CategoriaCreate(nombre="Periféricos"), self.admin.id_usuario)
        prod_srv = ProductoService(self.db)

        prod = prod_srv.registrar(
            ProductoCreate(
                codigo="MOU-001",
                nombre="Mouse inalámbrico",
                costo_actual=Decimal("35000.00"),
                precio_venta=Decimal("55000.00"),
                stock_actual=3,
                stock_minimo=5,
                id_categoria=cat.id_categoria,
            ),
            self.admin.id_usuario,
        )

        with self.assertRaises(ConflictoNegocioError):
            prod_srv.registrar(
                ProductoCreate(
                    codigo="mou-001",
                    nombre="Duplicado",
                    costo_actual=Decimal("10000"),
                    precio_venta=Decimal("20000"),
                    id_categoria=cat.id_categoria,
                ),
                self.admin.id_usuario,
            )

        with self.assertRaises(ValidationError):
            ProductoCreate(
                codigo="MOU-NEG",
                nombre="Inválido",
                costo_actual=Decimal("-1"),
                precio_venta=Decimal("1000"),
                id_categoria=cat.id_categoria,
            )

        existencia = prod_srv.consultar_existencia(prod.id_producto)
        self.assertEqual(existencia.stock_actual, 3)
        self.assertTrue(existencia.stock_bajo)

    def test_03_compras_ventas_transacciones_acid_y_rollback_sobreventa(self):
        cat = CategoriaService(self.db).registrar(CategoriaCreate(nombre="Tecnología"), self.admin.id_usuario)
        prov = ProveedorService(self.db).registrar(
            ProveedorCreate(documento="900123456-1", nombre="Mayorista Tech SAS"),
            self.admin.id_usuario,
        )
        cli = ClienteService(self.db).registrar(
            ClienteCreate(documento="1020304050", nombre="Cliente General"),
            self.admin.id_usuario,
        )

        prod_srv = ProductoService(self.db)
        datos = [
            ("PRD-01", "Portátil", Decimal("2000000"), Decimal("2500000"), 3),
            ("PRD-02", "Mouse inalámbrico", Decimal("35000"), Decimal("55000"), 5),
            ("PRD-03", "Teclado mecánico", Decimal("120000"), Decimal("180000"), 4),
            ("PRD-04", "Monitor", Decimal("650000"), Decimal("850000"), 3),
        ]
        ids = {}
        for cod, nom, costo, precio, smin in datos:
            p = prod_srv.registrar(
                ProductoCreate(
                    codigo=cod,
                    nombre=nom,
                    costo_actual=costo,
                    precio_venta=precio,
                    stock_actual=0,
                    stock_minimo=smin,
                    id_categoria=cat.id_categoria,
                ),
                self.admin.id_usuario,
            )
            ids[cod] = p.id_producto

        compra = CompraService(self.db).registrar_compra(
            CompraCreate(
                id_proveedor=prov.id_proveedor,
                observacion="Compra inicial reto integrador",
                detalles=[
                    DetalleCompraIn(id_producto=ids["PRD-01"], cantidad=10, costo_unitario=Decimal("2000000")),
                    DetalleCompraIn(id_producto=ids["PRD-02"], cantidad=20, costo_unitario=Decimal("35000")),
                    DetalleCompraIn(id_producto=ids["PRD-03"], cantidad=15, costo_unitario=Decimal("120000")),
                    DetalleCompraIn(id_producto=ids["PRD-04"], cantidad=8, costo_unitario=Decimal("650000")),
                ],
            ),
            self.admin.id_usuario,
        )
        self.assertEqual(compra.total, Decimal("27700000.00"))
        self.assertEqual(compra.estado, "CONFIRMADA")

        venta_srv = VentaService(self.db)
        with self.assertRaises(StockInsuficienteError):
            venta_srv.registrar_venta(
                VentaCreate(
                    id_cliente=cli.id_cliente,
                    detalles=[
                        DetalleVentaIn(id_producto=ids["PRD-02"], cantidad=3),
                        DetalleVentaIn(id_producto=ids["PRD-01"], cantidad=50),
                    ],
                ),
                self.admin.id_usuario,
            )

        # ROLLBACK dejó intactas las 20 unidades de Mouse
        self.assertEqual(prod_srv.consultar_existencia(ids["PRD-02"]).stock_actual, 20)

        venta = venta_srv.registrar_venta(
            VentaCreate(
                id_cliente=cli.id_cliente,
                detalles=[
                    DetalleVentaIn(id_producto=ids["PRD-01"], cantidad=2),
                    DetalleVentaIn(id_producto=ids["PRD-02"], cantidad=3),
                    DetalleVentaIn(id_producto=ids["PRD-03"], cantidad=1),
                    DetalleVentaIn(id_producto=ids["PRD-04"], cantidad=2),
                ],
            ),
            self.admin.id_usuario,
        )
        self.assertEqual(venta.total, Decimal("7045000.00"))

        stocks = {p.codigo: p.stock_actual for p in self.db.query(Producto).all()}
        self.assertEqual(stocks, {"PRD-01": 8, "PRD-02": 17, "PRD-03": 14, "PRD-04": 6})

        resumen = ReporteService(self.db).obtener_resumen()
        self.assertEqual(resumen.utilidad_bruta, Decimal("1520000.00"))

    def test_04_inventario_entradas_salidas_y_alertas_stock_bajo(self):
        cat = CategoriaService(self.db).registrar(CategoriaCreate(nombre="Accesorios"), self.admin.id_usuario)
        prod = ProductoService(self.db).registrar(
            ProductoCreate(
                codigo="CAB-01",
                nombre="Cable HDMI",
                costo_actual=Decimal("15000"),
                precio_venta=Decimal("28000"),
                stock_actual=5,
                stock_minimo=4,
                id_categoria=cat.id_categoria,
            ),
            self.admin.id_usuario,
        )

        inv_srv = InventarioService(self.db)
        mov = inv_srv.registrar_ajuste(
            MovimientoCreate(
                id_producto=prod.id_producto,
                tipo="SALIDA",
                cantidad=2,
                observacion="Ajuste por muestra comercial",
            ),
            self.admin.id_usuario,
        )
        self.assertEqual(mov.cantidad, 2)
        self.assertEqual(ProductoService(self.db).consultar_existencia(prod.id_producto).stock_actual, 3)

        alertas = inv_srv.consultar_alertas_stock_bajo()
        self.assertEqual(len(alertas), 1)
        self.assertEqual(alertas[0].codigo, "CAB-01")


if __name__ == "__main__":
    unittest.main()
