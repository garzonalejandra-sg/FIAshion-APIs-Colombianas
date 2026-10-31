from app.models import Cliente as ClienteModel
from app.domain.entities import Cliente

class SqlClienteRepository:
    def __init__(self, session):
        self.session = session

    def crear(self, cliente: Cliente) -> Cliente:
        row = ClienteModel(nombre=cliente.nombre, departamento=cliente.departamento,
                           municipio=cliente.municipio, codigo_postal=cliente.codigo_postal)
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return Cliente(nombre=row.nombre, departamento=row.departamento, municipio=row.municipio, codigo_postal=row.codigo_postal, id_cliente=row.id_cliente)

    def listar(self):
        return [Cliente(nombre=r.nombre, departamento=r.departamento, municipio=r.municipio, codigo_postal=r.codigo_postal, id_cliente=r.id_cliente)
                for r in self.session.query(ClienteModel).all()]
