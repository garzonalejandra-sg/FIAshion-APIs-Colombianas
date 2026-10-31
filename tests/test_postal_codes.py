from app.infrastructure.external.colombia_data import ColombiaDataClient


def test_codigos_postales_busca_ciudad_por_departamento_y_devuelve_lista(monkeypatch):
    client = ColombiaDataClient()
    calls = []

    class Response:
        def __init__(self, data): self.data = data
        def json(self): return self.data

    def fake_get(url, params=None, timeout=20.0):
        calls.append(url)
        if "/Department/name/" in url:
            return Response({"id": 10, "name": "Cundinamarca"})
        if "/Department/10/cities" in url:
            return Response([{"id": 42, "name": "Cota", "department": {"name": "Cundinamarca"}}])
        return Response([{"id": 7, "cityId": 42, "code": "250010"}])

    monkeypatch.setattr(client, "_get_json", fake_get)
    result = client.codigos_postales("Cota", "Cundinamarca")
    assert result["city_id"] == 42
    assert result["codigos_postales"][0]["code"] == "250010"
    assert len(calls) == 3
    assert not any("City/name/" in url for url in calls)


def test_codigos_postales_usa_busqueda_si_falla_ruta_departamento(monkeypatch):
    client = ColombiaDataClient()
    calls = []

    class Response:
        def __init__(self, data): self.data = data
        def json(self): return self.data

    def fake_get(url, params=None, timeout=20.0):
        calls.append(url)
        if "/Department/name/" in url:
            raise RuntimeError("Servicio temporalmente no disponible")
        if "/City/search/" in url:
            return Response([{"id": 42, "name": "Cota", "department": {"name": "Cundinamarca"}}])
        return Response([{"code": "250010", "cityId": 42}])

    monkeypatch.setattr(client, "_get_json", fake_get)
    result = client.codigos_postales("Cota", "Cundinamarca")
    assert result["cantidad"] == 1
    assert any("City/search/Cota" in url for url in calls)
