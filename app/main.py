from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from app.database import Base, engine
from app.errors import register_error_handlers
from app.routers import productos, clientes, colombia

Base.metadata.create_all(bind=engine)
# Migración sencilla para bases SQLite existentes: agrega el código postal sin borrar clientes.
from sqlalchemy import inspect, text
if engine.dialect.name == "sqlite":
    columns = {column["name"] for column in inspect(engine).get_columns("clientes")}
    if "codigo_postal" not in columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE clientes ADD COLUMN codigo_postal VARCHAR(10)"))

app = FastAPI(
    title="FIAshion API",
    version="2.0.0",
    description="API REST para catálogo de ropa, DIVIPOLA y consulta de códigos postales de Colombia."
)
register_error_handlers(app)
app.include_router(productos.router)
app.include_router(clientes.router)
app.include_router(colombia.router)

@app.get("/", tags=["Estado"])
def health():
    return {"status": "ok", "service": "FIAshion API"}
