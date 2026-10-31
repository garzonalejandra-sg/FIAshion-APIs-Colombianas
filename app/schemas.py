from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class ProductoBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    descripcion: str = Field("", max_length=300)
    precio: float = Field(..., gt=0)
    talla: str = "M"
    genero: str = "unisex"
    categoria: str = "general"
    estilo: str = "casual"
    disponible: bool = True

class ProductoCreate(ProductoBase):
    pass

class ProductoOut(ProductoBase):
    model_config = ConfigDict(from_attributes=True)
    id_producto: int

class ClienteCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=120)
    departamento: str = Field(..., min_length=1, max_length=100)
    municipio: Optional[str] = None
    codigo_postal: Optional[str] = Field(None, min_length=5, max_length=10)

class ClienteOut(ClienteCreate):
    model_config = ConfigDict(from_attributes=True)
    id_cliente: int

class ErrorOut(BaseModel):
    status: int
    message: str
    timestamp: str

class ValidationErrorOut(ErrorOut):
    details: list[dict]
