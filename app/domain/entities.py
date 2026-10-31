from dataclasses import dataclass
from typing import Optional

@dataclass
class Cliente:
    nombre: str
    departamento: str
    municipio: Optional[str] = None
    codigo_postal: Optional[str] = None
    id_cliente: Optional[int] = None
