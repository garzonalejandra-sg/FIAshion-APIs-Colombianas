from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import ClienteCreate, ClienteOut
from app.domain.entities import Cliente
from app.application.cliente_service import ClienteService
from app.infrastructure.repositories.sql_cliente_repository import SqlClienteRepository

router = APIRouter(prefix="/api/v1/clientes", tags=["Clientes"])

@router.post("", response_model=ClienteOut, status_code=201)
def crear_cliente(datos: ClienteCreate, db: Session = Depends(get_db)):
    service = ClienteService(SqlClienteRepository(db))
    cliente = service.registrar(Cliente(**datos.model_dump()))
    return ClienteOut(id_cliente=cliente.id_cliente, nombre=cliente.nombre,
                      departamento=cliente.departamento, municipio=cliente.municipio,
                      codigo_postal=cliente.codigo_postal)

@router.get("", response_model=list[ClienteOut])
def listar_clientes(db: Session = Depends(get_db)):
    return db.query(__import__("app.models", fromlist=["Cliente"]).Cliente).all()
