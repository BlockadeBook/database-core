from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.point.dtos import CoordinatesDto, PointDto
from app.point.service import PointService

router = APIRouter(prefix="/points")


@router.post("/")
def create(dto: PointDto, db: Session = Depends(get_db)):
    dto.validate_ids(db)
    service = PointService(db)
    return service.create(dto)


@router.get("/{id}")
def get_one(id: int, extended: bool = True, db: Session = Depends(get_db)):
    service = PointService(db)
    res = service.get_by_id(id, extended)
    if res is None:
        raise HTTPException(404)
    return res


@router.post("/{id}/coordinates")
def create_coordinates(dto: CoordinatesDto, id: int, db: Session = Depends(get_db)):
    service = PointService(db)
    if not service.exists(id):
        raise HTTPException(404)
    return service.create_coordinates(id, dto)


@router.get("/{id}/notes")
def get_notes(id: int, db: Session = Depends(get_db)):
    service = PointService(db)
    res = service.get_notes(id)
    if res is None:
        raise HTTPException(404)
    return res


@router.get("/{id}/coordinates")
def get_coordinates(id: int, db: Session = Depends(get_db)):
    service = PointService(db)
    return service.get_coordinates(id)


@router.get("/filters")
def get_filters(db: Session = Depends(get_db)):
    service = PointService(db)
    return service.get_filters()
