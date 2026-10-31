from app.domain.entities import Cliente
from app.domain.repositories import ClienteRepository

class ClienteService:
    def __init__(self, repository: ClienteRepository):
        self.repository = repository

    def registrar(self, cliente: Cliente) -> Cliente:
        if not cliente.nombre.strip() or not cliente.departamento.strip():
            raise ValueError("Nombre y departamento son obligatorios")
        return self.repository.crear(cliente)

    def listar(self):
        return self.repository.listar()
