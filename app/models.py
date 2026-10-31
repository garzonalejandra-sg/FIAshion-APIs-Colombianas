from sqlalchemy import String, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Producto(Base):
    __tablename__ = "productos"

    id_producto: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    descripcion: Mapped[str] = mapped_column(String(300), default="")
    precio: Mapped[float] = mapped_column(Float)
    talla: Mapped[str] = mapped_column(String(10), default="M")
    genero: Mapped[str] = mapped_column(String(20), default="unisex")
    categoria: Mapped[str] = mapped_column(String(50), default="general")
    estilo: Mapped[str] = mapped_column(String(50), default="casual")
    disponible: Mapped[bool] = mapped_column(Boolean, default=True)


class Cliente(Base):
    __tablename__ = "clientes"

    id_cliente: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120))
    departamento: Mapped[str] = mapped_column(String(100), index=True)
    municipio: Mapped[str] = mapped_column(String(100), default="")
    codigo_postal: Mapped[str | None] = mapped_column(String(10), nullable=True)
