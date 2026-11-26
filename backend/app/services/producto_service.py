from sqlalchemy.orm import Session
from app.core.exceptions import ConflictoNegocioError, RecursoNoEncontradoError, TechStoreException
from app.models.inventario import MovimientoInventario
from app.models.producto import Producto
from app.repositories.auditoria_repo import AuditoriaRepository
from app.repositories.categoria_repo import CategoriaRepository
from app.repositories.inventario_repo import InventarioRepository
from app.repositories.producto_repo import ProductoRepository
from app.schemas.producto import ExistenciaProductoOut, ProductoCreate, ProductoUpdate


class ProductoService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ProductoRepository(db)
        self.cat_repo = CategoriaRepository(db)
        self.inv_repo = InventarioRepository(db)
        self.audit = AuditoriaRepository(db)

    def registrar(self, data: ProductoCreate, id_usuario: int) -> Producto:
        if self.repo.get_by_codigo(data.codigo):
            raise ConflictoNegocioError(f"El código de producto '{data.codigo}' ya se encuentra registrado.")
        categoria = self.cat_repo.get_by_id(data.id_categoria)
        if not categoria:
            raise RecursoNoEncontradoError(f"La categoría con ID {data.id_categoria} no existe.")
        if not categoria.activa:
            raise TechStoreException(f"La categoría '{categoria.nombre}' está desactivada.", status_code=400)

        try:
            producto = Producto(
                codigo=data.codigo,
                nombre=data.nombre,
                descripcion=data.descripcion,
                id_categoria=data.id_categoria,
                precio_venta=data.precio_venta,
                costo_actual=data.costo_actual,
                stock_actual=data.stock_actual,
                stock_minimo=data.stock_minimo,
                activo=True,
            )
            self.repo.crear(producto)

            if data.stock_actual > 0:
                self.inv_repo.registrar_movimiento(
                    MovimientoInventario(
                        id_producto=producto.id_producto,
                        id_usuario=id_usuario,
                        tipo="ENTRADA",
                        cantidad=data.stock_actual,
                        observacion=f"Saldo inicial del producto {producto.codigo}",
                    )
                )

            self.audit.registrar(
                accion="CREAR_PRODUCTO",
                modulo="PRODUCTOS",
                detalle=f"Producto '{producto.codigo} - {producto.nombre}' registrado con stock={producto.stock_actual}",
                id_usuario=id_usuario,
            )
            self.db.commit()
            self.db.refresh(producto)
            return producto
        except Exception:
            self.db.rollback()
            raise

    def listar(
        self,
        id_categoria: int | None = None,
        solo_activos: bool = False,
        q: str | None = None,
    ) -> list[Producto]:
        return self.repo.listar(id_categoria=id_categoria, solo_activos=solo_activos, q=q)

    def consultar(self, id_producto: int) -> Producto:
        producto = self.repo.get_by_id(id_producto)
        if not producto:
            raise RecursoNoEncontradoError(f"Producto con ID {id_producto} no encontrado.")
        return producto

    def actualizar(self, id_producto: int, data: ProductoUpdate, id_usuario: int | None = None) -> Producto:
        producto = self.consultar(id_producto)
        if data.codigo and data.codigo.lower() != producto.codigo.lower():
            dup = self.repo.get_by_codigo(data.codigo)
            if dup and dup.id_producto != id_producto:
                raise ConflictoNegocioError(f"El código de producto '{data.codigo}' ya pertenece a otro producto.")
        if data.id_categoria is not None:
            cat = self.cat_repo.get_by_id(data.id_categoria)
            if not cat:
                raise RecursoNoEncontradoError(f"La categoría con ID {data.id_categoria} no existe.")
            if not cat.activa:
                raise TechStoreException(f"La categoría '{cat.nombre}' está desactivada.", status_code=400)

        try:
            for campo, valor in data.model_dump(exclude_unset=True).items():
                setattr(producto, campo, valor)
            self.audit.registrar(
                accion="ACTUALIZAR_PRODUCTO",
                modulo="PRODUCTOS",
                detalle=f"Producto ID {id_producto} ('{producto.codigo}') actualizado",
                id_usuario=id_usuario,
            )
            self.db.commit()
            self.db.refresh(producto)
            return producto
        except Exception:
            self.db.rollback()
            raise

    def desactivar(self, id_producto: int, id_usuario: int | None = None) -> Producto:
        producto = self.consultar(id_producto)
        try:
            producto.activo = False
            self.audit.registrar(
                accion="DESACTIVAR_PRODUCTO",
                modulo="PRODUCTOS",
                detalle=f"Producto ID {id_producto} ('{producto.codigo}') desactivado",
                id_usuario=id_usuario,
            )
            self.db.commit()
            self.db.refresh(producto)
            return producto
        except Exception:
            self.db.rollback()
            raise

    def consultar_existencia(self, id_producto: int) -> ExistenciaProductoOut:
        p = self.consultar(id_producto)
        return ExistenciaProductoOut(
            id_producto=p.id_producto,
            codigo=p.codigo,
            nombre=p.nombre,
            stock_actual=p.stock_actual,
            stock_minimo=p.stock_minimo,
            stock_bajo=p.stock_bajo,
            unidades_faltantes=max(0, p.stock_minimo - p.stock_actual),
            activo=p.activo,
        )

    def listar_existencias(self, solo_activos: bool = True) -> list[ExistenciaProductoOut]:
        productos = self.repo.listar(solo_activos=solo_activos)
        return [
            ExistenciaProductoOut(
                id_producto=p.id_producto,
                codigo=p.codigo,
                nombre=p.nombre,
                stock_actual=p.stock_actual,
                stock_minimo=p.stock_minimo,
                stock_bajo=p.stock_bajo,
                unidades_faltantes=max(0, p.stock_minimo - p.stock_actual),
                activo=p.activo,
            )
            for p in productos
        ]
