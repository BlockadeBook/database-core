"""Generic CRUD router for `ExtendedBaseClass` taxonomies (id + name)."""
from typing import Type

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.base.models import Base
from app.database import get_db


class NamedDto(BaseModel):
    name: str


def make_named_taxonomy_router(model: Type[Base], pk_field: str) -> APIRouter:
    """Build a router with GET list, POST, PATCH, DELETE for a name-only taxonomy."""
    r = APIRouter()

    @r.get("/")
    def list_all(db: Session = Depends(get_db)):
        return db.query(model).all()

    @r.post("/", status_code=201)
    def create(dto: NamedDto, db: Session = Depends(get_db)):
        item = model(name=dto.name)
        db.add(item)
        try:
            db.commit()
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(409, str(e.orig))
        db.refresh(item)
        return item

    @r.patch("/{id}")
    def update(id: int, dto: NamedDto, db: Session = Depends(get_db)):
        item = db.query(model).filter(getattr(model, pk_field) == id).first()
        if item is None:
            raise HTTPException(404)
        item.name = dto.name
        try:
            db.commit()
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(409, str(e.orig))
        db.refresh(item)
        return item

    @r.delete("/{id}", status_code=204)
    def delete(id: int, db: Session = Depends(get_db)):
        item = db.query(model).filter(getattr(model, pk_field) == id).first()
        if item is None:
            raise HTTPException(404)
        try:
            db.delete(item)
            db.commit()
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(409, str(e.orig))

    return r
