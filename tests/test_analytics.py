import pytest
duckdb = pytest.importorskip("duckdb")
from app.infrastructure.analytics.duckdb_service import AnalyticsService

def test_consultas_analiticas():
    service = AnalyticsService()
    service.cargar_poblacion([
        {"departamento": "A", "poblacion": "1000", "anio": "2024"},
        {"departamento": "B", "poblacion": "2000", "anio": "2024"},
        {"departamento": "dato incompleto", "poblacion": "no-numero"}
    ])
    service.cargar_clientes([("A", 10)])
    assert service.poblacion_por_departamento()[0]["departamento"] == "B"
    result = service.clientes_vs_poblacion()
    assert next(x for x in result if x["departamento"] == "A")["clientes"] == 10

