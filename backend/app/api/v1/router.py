from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    categorias,
    compras,
    inventario,
    productos,
    reportes,
    terceros,
    ventas,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(categorias.router)
api_router.include_router(productos.router)
api_router.include_router(terceros.router)
api_router.include_router(compras.router)
api_router.include_router(ventas.router)
api_router.include_router(inventario.router)
api_router.include_router(reportes.router)
