from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Producto
from app.schemas import ProductoCreate, ProductoOut, ErrorOut, ValidationErrorOut

router = APIRouter(prefix="/api/v1/productos", tags=["Products"])

NOT_FOUND = {404: {"model": ErrorOut, "description": "Product not found"}}
INVALID = {422: {"model": ValidationErrorOut, "description": "Invalid data"}}


@router.post("", response_model=ProductoOut, status_code=status.HTTP_201_CREATED,
             responses=INVALID,
             summary="Create a product",
             description="Creates a new product in the catalog and returns it with its id.")
def crear(datos: ProductoCreate, db: Session = Depends(get_db)):
    producto = Producto(**datos.model_dump())
    db.add(producto)
    db.commit()
    db.refresh(producto)
    return producto


@router.get("", response_model=List[ProductoOut],
            summary="List all products",
            description="Returns every product in the catalog.")
def listar(db: Session = Depends(get_db)):
    return db.scalars(select(Producto)).all()


@router.get("/{producto_id}", response_model=ProductoOut,
            responses={**NOT_FOUND, **INVALID},
            summary="Get a product by id",
            description="Returns one product. Responds 404 if the id does not exist.")
def obtener(producto_id: int, db: Session = Depends(get_db)):
    producto = db.get(Producto, producto_id)
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@router.put("/{producto_id}", response_model=ProductoOut,
            responses={**NOT_FOUND, **INVALID},
            summary="Update a product",
            description="Replaces the data of an existing product.")
def actualizar(producto_id: int, datos: ProductoCreate, db: Session = Depends(get_db)):
    producto = db.get(Producto, producto_id)
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    for campo, valor in datos.model_dump().items():
        setattr(producto, campo, valor)
    db.commit()
    db.refresh(producto)
    return producto


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT,
               responses={**NOT_FOUND, **INVALID},
               summary="Delete a product",
               description="Deletes a product. Responds 204 with no body.")
def eliminar(producto_id: int, db: Session = Depends(get_db)):
    producto = db.get(Producto, producto_id)
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    db.delete(producto)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)