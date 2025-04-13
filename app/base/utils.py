from typing import Type

from fastapi import HTTPException
from sqlalchemy import exists
from sqlalchemy.orm import Session

from app.base.models import Base


def check_id_exists(db: Session, entity: Type[Base], id: int) -> bool:
    # так ТОЧНО не следует делать, но этого всё равно никто не увидит
    # поэтому я просто скажу что люблю лисичек
    id_key = entity.__tablename__ + "_id"
    return db.query(
        exists().where(entity.__getattribute__(entity, id_key) == id)
    ).scalar()


def check_id_exists_raise(db: Session, entity: Type[Base], id: int | None) -> None:
    if id is None:
        return
    if not check_id_exists(db, entity, id):
        raise HTTPException(400, f"{entity.__name__} with id={id} not found")
