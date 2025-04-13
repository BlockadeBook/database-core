from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.base.utils import check_id_exists_raise
from app.point.models import PointSubSubType, PointSubType, PointType, Rayon


class PointDto(BaseModel):
    rayon_id: int
    street: str
    building: str
    latitude: float
    longitude: float | None
    point_type_id: int
    point_subtype_id: int | None
    point_subsubtype_id: int | None
    name: str
    description: str | None

    def validate_ids(self, db: Session) -> None:
        check_id_exists_raise(db, Rayon, self.rayon_id)
        check_id_exists_raise(db, PointType, self.point_type_id)
        check_id_exists_raise(db, PointSubType, self.point_subtype_id)
        check_id_exists_raise(db, PointSubSubType, self.point_subsubtype_id)


class CoordinatesDto(BaseModel):
    latitude: float
    longitude: float  # TODO: validate coordinates
