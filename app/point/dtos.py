from typing import List, Optional

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.base.utils import check_id_exists_raise
from app.point.models import PointSubSubType, PointSubType, PointType, Rayon


class PointDto(BaseModel):
    rayon_id: int | None = None
    street: str = ""
    building: str = ""
    latitude: float | None = None
    longitude: float | None = None
    point_type_id: int
    point_subtype_id: int | None = None
    point_subsubtype_id: int | None = None
    name: str
    description: str | None = None

    def validate_ids(self, db: Session) -> None:
        check_id_exists_raise(db, Rayon, self.rayon_id)
        check_id_exists_raise(db, PointType, self.point_type_id)
        check_id_exists_raise(db, PointSubType, self.point_subtype_id)
        check_id_exists_raise(db, PointSubSubType, self.point_subsubtype_id)


class CoordinatesDto(BaseModel):
    latitude: float
    longitude: float  # TODO: validate coordinates


class PointFilterParams(BaseModel):
    search: Optional[str] = None
    rayon_ids: List[int] = []
    point_type_ids: List[int] = []
    point_subtype_ids: List[int] = []
    point_subsubtype_ids: List[int] = []


class PointTypeDto(BaseModel):
    name: str
    has_fixed_coordinates: bool
    has_address: bool


class PointSubTypeDto(BaseModel):
    name: str
    point_type_id: Optional[int] = None

    def validate_ids(self, db: Session) -> None:
        check_id_exists_raise(db, PointType, self.point_type_id)


class PointSubSubTypeDto(BaseModel):
    name: str
    point_subtype_id: Optional[int] = None

    def validate_ids(self, db: Session) -> None:
        check_id_exists_raise(db, PointSubType, self.point_subtype_id)
