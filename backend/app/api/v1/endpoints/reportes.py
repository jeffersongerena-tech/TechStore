from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import require_roles
from app.database.connection import get_db
from app.models.usuario import Usuario
from app.schemas.reporte import AuditoriaOut, ResumenComercialOut
from app.services.reporte_service import ReporteService

router = APIRouter(prefix="/reportes", tags=["Reportes y Auditoría"])


@router.get(
    "/resumen",
    response_model=ResumenComercialOut,
    summary="Indicadores generales de compras, ventas, costo vendido, utilidad bruta y top productos",
)
def obtener_resumen_comercial(
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles("ADMINISTRADOR")),
):
    return ReporteService(db).obtener_resumen()


@router.get(
    "/auditoria",
    response_model=list[AuditoriaOut],
    summary="Consultar bitácora de auditoría del sistema",
)
def consultar_auditoria(
    modulo: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles("ADMINISTRADOR")),
):
    return ReporteService(db).listar_auditoria(modulo=modulo, limit=limit)
