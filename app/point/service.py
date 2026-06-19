from sqlalchemy import exists, or_
from sqlalchemy.orm import Session, joinedload

from app.point.dtos import (
    CoordinatesDto,
    PointDto,
    PointFilterParams,
    PointSubSubTypeDto,
    PointSubTypeDto,
    PointTypeDto,
)
from app.authors.models import Author, AuthorToPoint
from app.notes.models import Diary, Note, NoteToPoint
from app.point.models import (
    Point,
    PointCoordinates,
    PointSubSubType,
    PointSubType,
    PointType,
    Rayon,
)


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

        # Координата необязательна: создаём её только если заданы и широта,
        # и долгота (составной PK таблицы координат не допускает NULL).
        if dto.latitude is not None and dto.longitude is not None:
            coordinates = PointCoordinates(
                latitude=dto.latitude, longitude=dto.longitude, point_id=point.point_id
            )
            self.db.add(coordinates)
            self.db.commit()
            self.db.refresh(point)

        return point

    def update(self, id: int, dto: PointDto):
        point = self.db.query(Point).filter(Point.point_id == id).first()
        if point is None:
            return None

        point.name = dto.name
        point.rayon_id = dto.rayon_id
        point.street = dto.street
        point.building = dto.building
        point.point_type_id = dto.point_type_id
        point.point_subtype_id = dto.point_subtype_id
        point.point_subsubtype_id = dto.point_subsubtype_id
        point.description = dto.description
        self.db.commit()

        # Координата хранится со составным PK (point_id, lat, lon) — «изменить»
        # строку нельзя, поэтому основную координату пересоздаём: удаляем
        # имеющиеся координаты места и кладём заданную. Панель работает с одной
        # основной координатой (как и форма добавления).
        if dto.latitude is not None and dto.longitude is not None:
            self.db.query(PointCoordinates).filter(
                PointCoordinates.point_id == id
            ).delete()
            self.db.add(
                PointCoordinates(
                    point_id=id, latitude=dto.latitude, longitude=dto.longitude
                )
            )
            self.db.commit()

        return self.get_by_id(id, extended=True)

    def delete_point(self, id: int):
        """Удаляет место. None — если места нет. ValueError — если к месту
        привязаны свидетельства (удаление блокируется)."""
        point = self.db.query(Point).filter(Point.point_id == id).first()
        if point is None:
            return None

        ref = self.db.query(NoteToPoint).filter(NoteToPoint.point_id == id).count()
        if ref > 0:
            raise ValueError(
                f"К месту привязаны свидетельства ({ref}). Сначала отвяжите их."
            )

        # Убираем координаты и связи автор-место, затем само место.
        self.db.query(PointCoordinates).filter(PointCoordinates.point_id == id).delete()
        self.db.query(AuthorToPoint).filter(AuthorToPoint.point_id == id).delete()
        self.db.delete(point)
        self.db.commit()
        return True

    def get_all(self, filters: PointFilterParams | None = None):
        q = self.db.query(Point).options(
            joinedload(Point.rayon),
            joinedload(Point.point_coordinates),
            joinedload(Point.point_type),
            joinedload(Point.point_subtype),
            joinedload(Point.point_subsubtype),
        )
        if filters is None:
            return self._with_note_coordinates(q.all())

        if filters.search:
            pattern = f"%{filters.search}%"
            q = q.filter(
                or_(
                    Point.name.ilike(pattern),
                    Point.street.ilike(pattern),
                    Point.description.ilike(pattern),
                )
            )
        if filters.rayon_ids:
            q = q.filter(Point.rayon_id.in_(filters.rayon_ids))
        if filters.point_type_ids:
            q = q.filter(Point.point_type_id.in_(filters.point_type_ids))
        if filters.point_subtype_ids:
            q = q.filter(Point.point_subtype_id.in_(filters.point_subtype_ids))
        if filters.point_subsubtype_ids:
            q = q.filter(Point.point_subsubtype_id.in_(filters.point_subsubtype_ids))
        return self._with_note_coordinates(q.all())

    def _with_note_coordinates(self, points):
        """Прикрепляет к каждой точке координаты её свидетельств из
        note_to_point (где они заданы вручную, т.е. место без фиксированной
        координаты). Это позволяет карте рисовать отдельный маркер на каждое
        свидетельство нефиксированного места."""
        if not points:
            return points
        ids = [p.point_id for p in points]
        rows = (
            self.db.query(
                NoteToPoint.point_id,
                NoteToPoint.note_id,
                NoteToPoint.latitude,
                NoteToPoint.longitude,
            )
            .filter(NoteToPoint.point_id.in_(ids), NoteToPoint.latitude.isnot(None))
            .all()
        )
        by_point: dict[int, list] = {}
        for point_id, note_id, lat, lon in rows:
            by_point.setdefault(point_id, []).append(
                {"note_id": note_id, "latitude": lat, "longitude": lon}
            )
        for point in points:
            point.note_coordinates = by_point.get(point.point_id, [])
        return points

    def create_point_type(self, dto: PointTypeDto) -> PointType:
        item = PointType(
            name=dto.name,
            has_fixed_coordinates=dto.has_fixed_coordinates,
            has_address=dto.has_address,
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def create_point_subtype(self, dto: PointSubTypeDto) -> PointSubType:
        item = PointSubType(name=dto.name, point_type_id=dto.point_type_id)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def create_point_subsubtype(self, dto: PointSubSubTypeDto) -> PointSubSubType:
        item = PointSubSubType(name=dto.name, point_subtype_id=dto.point_subtype_id)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

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
        res = (
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
        if res is not None:
            self._with_note_coordinates([res])
        return res

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
        if not self.exists(point_id):
            return None
        # Свидетельства места с подгруженными тегами, типом, темпоральностью
        # и именем автора. Возвращаем плоский формат, который ждёт фронтенд
        # (note_type / temporality / tags как {id, name}).
        rows = (
            self.db.query(
                Note,
                Author.first_name,
                Author.middle_name,
                Author.last_name,
            )
            .join(NoteToPoint, NoteToPoint.note_id == Note.note_id)
            .join(Diary, Diary.diary_id == Note.diary_id)
            .join(Author, Author.author_id == Diary.author_id)
            .filter(NoteToPoint.point_id == point_id)
            .options(
                joinedload(Note.tags),
                joinedload(Note.note_types),
                joinedload(Note.temporalities),
            )
            .order_by(Note.created_at)
            .all()
        )
        result = []
        for note, first_name, middle_name, last_name in rows:
            result.append(
                {
                    "note_id": note.note_id,
                    "diary_id": note.diary_id,
                    "created_at": note.created_at,
                    "citation": note.citation,
                    "source": note.source,
                    "note_types": [
                        {"id": t.note_type_id, "name": t.name}
                        for t in note.note_types
                    ],
                    "temporalities": [
                        {"id": t.temporality_id, "name": t.name}
                        for t in note.temporalities
                    ],
                    "tags": [
                        {"id": tag.tag_id, "name": tag.name} for tag in note.tags
                    ],
                    "first_name": first_name,
                    "middle_name": middle_name,
                    "last_name": last_name,
                }
            )
        return result

    def exists(self, point_id: int) -> bool:
        return self.db.query(exists().where(Point.point_id == point_id)).scalar()
