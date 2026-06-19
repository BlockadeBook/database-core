from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.base.query_params import parse_int_csv
from app.base.taxonomy import make_named_taxonomy_router
from app.database import get_db
from app.point.dtos import (
    CoordinatesDto,
    PointDto,
    PointFilterParams,
    PointSubSubTypeDto,
    PointSubTypeDto,
    PointTypeDto,
)
from app.point.models import Rayon
from app.point.service import PointService

router = APIRouter(prefix="/points")


@router.get("/filters")
def get_filters(db: Session = Depends(get_db)):
    service = PointService(db)
    return service.get_filters()


@router.post("/")
def create(dto: PointDto, db: Session = Depends(get_db)):
    dto.validate_ids(db)
    service = PointService(db)
    try:
        return service.create(dto)
    except Exception as e:
        raise HTTPException(400, str(e))


@router.patch("/{id}")
def update(id: int, dto: PointDto, db: Session = Depends(get_db)):
    dto.validate_ids(db)
    service = PointService(db)
    res = service.update(id, dto)
    if res is None:
        raise HTTPException(404)
    return res


@router.delete("/{id}", status_code=204)
def delete(id: int, db: Session = Depends(get_db)):
    service = PointService(db)
    try:
        res = service.delete_point(id)
    except ValueError as e:
        raise HTTPException(409, str(e))
    if res is None:
        raise HTTPException(404)


@router.get("/")
def get_all(
    search: Optional[str] = None,
    rayon_ids: Optional[str] = None,
    point_type_ids: Optional[str] = None,
    point_subtype_ids: Optional[str] = None,
    point_subsubtype_ids: Optional[str] = None,
    db: Session = Depends(get_db),
):
    filters = PointFilterParams(
        search=search,
        rayon_ids=parse_int_csv(rayon_ids),
        point_type_ids=parse_int_csv(point_type_ids),
        point_subtype_ids=parse_int_csv(point_subtype_ids),
        point_subsubtype_ids=parse_int_csv(point_subsubtype_ids),
    )
    service = PointService(db)
    return service.get_all(filters)


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


# Taxonomies — rayon is name-only
router.include_router(
    make_named_taxonomy_router(Rayon, "rayon_id"), prefix="/rayons"
)


# Point type / subtype / subsubtype have extra fields, custom routes
@router.post("/point-types", status_code=201)
def create_point_type(dto: PointTypeDto, db: Session = Depends(get_db)):
    service = PointService(db)
    return service.create_point_type(dto)


@router.post("/point-subtypes", status_code=201)
def create_point_subtype(dto: PointSubTypeDto, db: Session = Depends(get_db)):
    dto.validate_ids(db)
    service = PointService(db)
    return service.create_point_subtype(dto)


@router.post("/point-subsubtypes", status_code=201)
def create_point_subsubtype(dto: PointSubSubTypeDto, db: Session = Depends(get_db)):
    dto.validate_ids(db)
    service = PointService(db)
    return service.create_point_subsubtype(dto)
