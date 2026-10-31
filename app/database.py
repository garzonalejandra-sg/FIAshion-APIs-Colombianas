import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fiashion.db")

# check_same_thread=False: FastAPI atiende peticiones en varios hilos
# y SQLite por defecto no lo permite.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db():
    """Abre una sesion por peticion y la cierra siempre al terminar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
