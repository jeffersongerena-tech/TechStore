from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import TechStoreException
from app.database.init_db import init_database

logger = logging.getLogger("techstore")


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        init_database()
        logger.info("Base de datos '%s' verificada y lista.", settings.DB_NAME)
    except Exception as exc:
        logger.warning(
            "No fue posible conectar con MySQL al iniciar (%s). "
            "Verifique que MySQL esté encendido en el Panel de Control de XAMPP.",
            exc,
        )
    yield


OPENAPI_TAGS = [
    {"name": "1. Categorías", "description": "Registrar, listar, consultar, actualizar y desactivar categorías."},
    {"name": "2. Productos", "description": "Gestión de catálogo, validaciones de precios/código único y consulta de existencias."},
    {"name": "3. Proveedores y Clientes", "description": "Registro, consulta y actualización de terceros comerciales."},
    {"name": "4. Compras", "description": "Registro transaccional de compras con aumento automático de inventario."},
    {"name": "5. Ventas", "description": "Registro transaccional de ventas con validación de stock, descuentos e impuestos."},
    {"name": "6. Inventario y Alertas", "description": "Entradas y salidas de kardex y consulta de alertas de stock bajo."},
    {"name": "Reportes y Auditoría", "description": "Indicadores financieros, utilidad bruta y bitácora de auditoría."},
    {"name": "Autenticación y Usuarios", "description": "Inicio de sesión JWT y gestión de usuarios por rol."},
]

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "API REST desacoplada para la gestión comercial de **TechStore** "
        "(Inventario, Compras, Ventas, Alertas y Auditoría con transacciones ACID)."
    ),
    openapi_tags=OPENAPI_TAGS,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(TechStoreException)
async def techstore_exception_handler(_: Request, exc: TechStoreException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"ok": False, "detail": exc.mensaje},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    errores = [
        {"campo": ".".join(str(loc) for loc in err["loc"] if loc != "body"), "mensaje": err["msg"]}
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={
            "ok": False,
            "detail": "Datos de entrada inválidos. Verifique campos obligatorios, precios >= 0 y cantidades > 0.",
            "errores": errores,
        },
    )


@app.get("/", tags=["Estado del Servicio"], summary="Verificar estado de la API")
def root():
    return {
        "ok": True,
        "mensaje": "API de TechStore funcionando correctamente",
        "version": settings.VERSION,
        "documentacion_swagger": "/docs",
    }


app.include_router(api_router, prefix=settings.API_V1_STR)
