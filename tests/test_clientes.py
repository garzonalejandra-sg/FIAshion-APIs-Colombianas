def test_registrar_cliente(client):
    response = client.post("/api/v1/clientes", json={
        "nombre": "Ana", "departamento": "CUNDINAMARCA", "municipio": "CHÍA", "codigo_postal": "250001"
    })
    assert response.status_code == 201
    assert response.json()["departamento"] == "CUNDINAMARCA"
    assert response.json()["codigo_postal"] == "250001"

def test_listar_clientes(client):
    client.post("/api/v1/clientes", json={
        "nombre": "Ana", "departamento": "CUNDINAMARCA"
    })
    response = client.get("/api/v1/clientes")
    assert response.status_code == 200
    assert len(response.json()) == 1
