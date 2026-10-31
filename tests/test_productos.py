# Las 3 pruebas de integracion que pide la guia (rutas -> logica -> base de datos).

def test_crear_y_consultar_producto(client):
    r = client.post("/api/v1/productos",
                    json={"nombre": "Camisa", "precio": 50000})
    assert r.status_code == 201
    id_ = r.json()["id_producto"]

    r2 = client.get(f"/api/v1/productos/{id_}")
    assert r2.status_code == 200
    assert r2.json()["nombre"] == "Camisa"


def test_producto_inexistente_da_404(client):
    r = client.get("/api/v1/productos/9999")
    assert r.status_code == 404
    assert r.json()["message"] == "Producto no encontrado"


def test_datos_invalidos_dan_422(client):
    r = client.post("/api/v1/productos", json={"nombre": "", "precio": -5})
    assert r.status_code == 422
