from sqlalchemy import exists
from sqlalchemy.orm import Session, joinedload

from app.point.dtos import CoordinatesDto, PointDto
from app.point.models import Point, PointCoordinates, PointSubType, PointType


class PointService:
    db: Session

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_filters(self):
        return (
            self.db.query(PointType)
            .options(
                joinedload(PointType.point_subtypes).joinedload(
                    PointSubType.point_subsubtypes
                )
            )
            .all()
        )

    def create(self, dto: PointDto):
        point = Point(
            name=dto.name,
            rayon_id=dto.rayon_id,
            street=dto.street,
            building=dto.building,
            point_type_id=dto.point_type_id,
            point_subtype_id=dto.point_subtype_id,
            point_subsubtype_id=dto.point_subsubtype_id,
            description=dto.description,
        )
        self.db.add(point)
        self.db.commit()
        self.db.refresh(point)

        coordinates = PointCoordinates(
            latitude=dto.latitude, longitude=dto.longitude, point_id=point.point_id
        )
        self.db.add(coordinates)
        self.db.commit()

        self.db.refresh(point)
        return point

    def get_by_id(self, id: int, extended: bool):
        if not extended:
            res = (
                self.db.query(Point)
                .filter(Point.point_id == id)
                .options(
                    joinedload(Point.point_type).load_only(
                        PointType.has_fixed_coordinates,
                        PointType.has_address,
                    )
                )
                .first()
            )
            if res is None:
                return None
            return {
                "point_id": res.point_id,
                "name": res.name,
                "has_fixed_coordinates": res.point_type.has_fixed_coordinates,
                "has_address": res.point_type.has_address,
            }
        return (
            self.db.query(Point)
            .options(
                joinedload(Point.rayon),
                joinedload(Point.point_coordinates),
                joinedload(Point.point_type),
                joinedload(Point.point_subtype),
                joinedload(Point.point_subsubtype),
            )
            .filter(Point.point_id == id)
            .first()
        )

    def create_coordinates(self, point_id: int, dto: CoordinatesDto):
        coordinates = PointCoordinates(
            point_id=point_id,
            latitude=dto.latitude,
            longitude=dto.longitude,
        )
        self.db.add(coordinates)
        self.db.commit()
        self.db.refresh(coordinates)
        return coordinates

    def get_coordinates(self, point_id: int):
        res = [
            i._asdict()
            for i in self.db.query(
                PointCoordinates.latitude, PointCoordinates.longitude
            )
            .filter(PointCoordinates.point_id == point_id)
            .all()
        ]
        return {"point_id": point_id, "coordinates": res}

    def get_notes(self, point_id: int):
        point = self.db.query(Point).filter(Point.point_id == point_id).first()
        if point is None:
            return None
        return point.notes

    def exists(self, point_id: int) -> bool:
        return self.db.query(exists().where(Point.point_id == point_id)).scalar()
