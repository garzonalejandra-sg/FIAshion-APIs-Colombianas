from fastapi import APIRouter, HTTPException, Query
from app.infrastructure.external.colombia_data import ColombiaDataClient

router = APIRouter(prefix="/api/v1/colombia", tags=["Datos de Colombia"])
client = ColombiaDataClient()

@router.get("/departamentos")
def departamentos():
    try:
        return client.departamentos()
    except Exception as exc:
        raise HTTPException(503, f"No fue posible consultar DIVIPOLA: {exc}")

@router.get("/municipios")
def municipios(departamento: str | None = None):
    try:
        return client.municipios(departamento)
    except Exception as exc:
        raise HTTPException(503, f"No fue posible consultar DIVIPOLA: {exc}")

@router.get("/codigos-postales", summary="Consultar códigos postales por municipio")
def codigos_postales(
    municipio: str = Query(..., min_length=2, description="Nombre del municipio, por ejemplo Chía"),
    departamento: str | None = Query(None, description="Departamento para evitar homónimos"),
):
    try:
        return client.codigos_postales(municipio, departamento)
    except ValueError as exc:
        raise HTTPException(404, str(exc))
    except Exception as exc:
        raise HTTPException(503, f"No fue posible consultar API Colombia: {exc}")
