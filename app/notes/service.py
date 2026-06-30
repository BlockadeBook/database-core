from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.authors.models import Author, Education
from app.notes.dtos import (
    DiaryDto,
    DiaryFilterParams,
    NoteDto,
    NoteFilterParams,
    TagDto,
)
from app.notes.models import (
    CityName,
    Diary,
    GeoName,
    Note,
    NoteToCityName,
    NoteToGeoName,
    NoteToNoteType,
    NoteToOrganization,
    NoteToPersonality,
    NoteToPoint,
    NoteToTag,
    NoteToTemporality,
    NoteType,
    Organization,
    Personality,
    Tag,
    Temporality,
)
from app.point.models import Point, PointCoordinates


class NoteService:
    db: Session

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_filters(self):
        return {
            "tags": self.db.query(Tag).all(),
            "note_types": self.db.query(NoteType).all(),
            "temporalities": self.db.query(Temporality).all(),
            # Новые справочники. organizations/city_names/geo_names выводятся
            # в фильтры карты; personalities — только для выбора в админке
            # (в фильтры карты не попадают).
            "organizations": self.db.query(Organization).all(),
            "city_names": self.db.query(CityName).all(),
            "geo_names": self.db.query(GeoName).all(),
            "personalities": self.db.query(Personality).all(),
        }

    @staticmethod
    def _serialize_note_list(note: Note) -> dict:
        """Плоский формат заметки для списка/фильтрации на клиенте:
        связи (тип, темпоральность, теги), id автора и привязанные точки."""
        return {
            "note_id": note.note_id,
            "diary_id": note.diary_id,
            "author_id": note.diary.author_id if note.diary else None,
            "created_at": note.created_at,
            "citation": note.citation,
            "source": note.source,
            "note_types": [
                {"id": t.note_type_id, "name": t.name} for t in note.note_types
            ],
            "temporalities": [
                {"id": t.temporality_id, "name": t.name} for t in note.temporalities
            ],
            "tags": [{"id": tag.tag_id, "name": tag.name} for tag in note.tags],
            "point_ids": [point.point_id for point in note.points],
        }

    def get_all(self, filters: NoteFilterParams | None = None):
        q = self.db.query(Note).options(
            joinedload(Note.note_types),
            joinedload(Note.temporalities),
            joinedload(Note.tags),
            joinedload(Note.points),
            joinedload(Note.diary),
        )
        if filters is None:
            return [self._serialize_note_list(note) for note in q.all()]

        if filters.search:
            pattern = f"%{filters.search}%"
            q = q.filter(
                or_(Note.citation.ilike(pattern), Note.source.ilike(pattern))
            )
        if filters.note_type_ids:
            q = q.join(NoteToNoteType).filter(
                NoteToNoteType.note_type_id.in_(filters.note_type_ids)
            )
        if filters.temporality_ids:
            q = q.join(NoteToTemporality).filter(
                NoteToTemporality.temporality_id.in_(filters.temporality_ids)
            )
        if filters.diary_ids:
            q = q.filter(Note.diary_id.in_(filters.diary_ids))
        if filters.author_ids:
            q = q.join(Diary, Note.diary_id == Diary.diary_id).filter(
                Diary.author_id.in_(filters.author_ids)
            )
        if filters.tag_ids:
            q = q.join(NoteToTag).filter(NoteToTag.tag_id.in_(filters.tag_ids))
        if filters.organization_ids:
            q = q.join(NoteToOrganization).filter(
                NoteToOrganization.organization_id.in_(filters.organization_ids)
            )
        if filters.city_name_ids:
            q = q.join(NoteToCityName).filter(
                NoteToCityName.city_name_id.in_(filters.city_name_ids)
            )
        if filters.geo_name_ids:
            q = q.join(NoteToGeoName).filter(
                NoteToGeoName.geo_name_id.in_(filters.geo_name_ids)
            )
        if filters.point_ids:
            q = q.join(NoteToPoint).filter(NoteToPoint.point_id.in_(filters.point_ids))
        if filters.date_from:
            q = q.filter(Note.created_at >= filters.date_from)
        if filters.date_to:
            q = q.filter(Note.created_at <= filters.date_to)
        return [self._serialize_note_list(note) for note in q.distinct().all()]

    def get_by_id(self, id: int, extended: bool):
        if not extended:
            return (
                self.db.query(
                    Note.note_id,
                    Note.citation,
                    Note.created_at,
                    Author.first_name,
                    Author.middle_name,
                    Author.last_name,
                )
                .join(Diary, Note.diary_id == Diary.diary_id)
                .join(Author, Diary.author_id == Author.author_id)
                .filter(Note.note_id == id)
                .first()
                ._asdict()  # type: ignore
            )

        return (
            self.db.query(
                Note,
                Author.first_name,
                Author.middle_name,
                Author.last_name,
            )
            .filter(Note.note_id == id)
            .options(
                joinedload(Note.temporalities),
                joinedload(Note.tags),
                joinedload(Note.note_types),
            )
            .first()
            ._asdict()  # type: ignore
        )

    def get_detailed_by_id(self, id: int):
        row = (self.db.query(
            Note,
            Author
        ).join(Diary, Diary.diary_id == Note.diary_id)
               .join(Author, Author.author_id == Diary.author_id)
               .options(joinedload(Note.note_types))
               .options(joinedload(Note.temporalities))
               .options(joinedload(Note.tags))
               .options(joinedload(Author.education))
               .options(joinedload(Author.family_status))
               .options(joinedload(Note.points).joinedload(Point.point_coordinates))
               .filter(Note.note_id == id).first())
        if row is None:
            return None

        note, author = row
        return {
            "note_id": note.note_id,
            "diary_id": note.diary_id,
            "created_at": note.created_at,
            "citation": note.citation,
            "source": note.source,
            "note_types": [
                {"id": t.note_type_id, "name": t.name} for t in note.note_types
            ],
            "temporalities": [
                {"id": t.temporality_id, "name": t.name} for t in note.temporalities
            ],
            "tags": [{"id": tag.tag_id, "name": tag.name} for tag in note.tags],
            "points": [
                {
                    "point_id": p.point_id,
                    "name": p.name,
                    "description": p.description,
                    "point_coordinates": [
                        {"latitude": c.latitude, "longitude": c.longitude}
                        for c in (p.point_coordinates or [])
                    ],
                }
                for p in note.points
            ],
            "author_id": author.author_id,
            "author_first_name": author.first_name or "",
            "author_middle_name": author.middle_name,
            "author_last_name": author.last_name or "",
            "author_sex": author.sex,
            "author_birth_date": author.birth_date,
            "author_biography": author.biography,
            "author_has_children": author.has_children,
            "author_family_status_id": author.family_status_id,
            "author_education": [
                {"id": e.education_id, "name": e.name} for e in author.education
            ],
            "author_family_status": (
                {
                    "id": author.family_status.family_status_id,
                    "name": author.family_status.name,
                }
                if author.family_status
                else None
            ),
        }

    def create_note(self, dto: NoteDto):
        diary = self.db.query(Diary).filter(Diary.author_id == dto.author_id).first()
        if diary is None:
            diary = self.create_diary(
                DiaryDto(
                    author_id=dto.author_id,
                    source="",
                    started_at=dto.created_at,
                    finished_at=dto.created_at,
                )
            )

        note = Note(
            diary_id=diary.diary_id,
            created_at=dto.created_at,
            citation=dto.citation,
            source=dto.source,
            localization_accuracy=dto.localization_accuracy,
            place_type=dto.place_type,
        )
        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)

        note.note_types.extend(
            self.db.query(NoteType)
            .filter(NoteType.note_type_id.in_(dto.note_type_ids))
            .all()
        )
        note.temporalities.extend(
            self.db.query(Temporality)
            .filter(Temporality.temporality_id.in_(dto.temporality_ids))
            .all()
        )

        for ntp in dto.note_to_points:
            self.db.add(
                NoteToPoint(
                    note_id=note.note_id,
                    point_id=ntp.point_id,
                    description=ntp.description,
                    latitude=ntp.latitude,
                    longitude=ntp.longitude,
                )
            )

        note.tags.extend(self.db.query(Tag).filter(Tag.tag_id.in_(dto.tag_ids)).all())

        # Новые тегоподобные графы.
        note.organizations.extend(
            self.db.query(Organization)
            .filter(Organization.organization_id.in_(dto.organization_ids))
            .all()
        )
        note.city_names.extend(
            self.db.query(CityName)
            .filter(CityName.city_name_id.in_(dto.city_name_ids))
            .all()
        )
        note.geo_names.extend(
            self.db.query(GeoName)
            .filter(GeoName.geo_name_id.in_(dto.geo_name_ids))
            .all()
        )
        note.personalities.extend(
            self.db.query(Personality)
            .filter(Personality.personality_id.in_(dto.personality_ids))
            .all()
        )

        self.db.commit()
        self.db.refresh(note)
        return note

    def update_note(self, id: int, dto: NoteDto):
        note = (
            self.db.query(Note)
            .options(joinedload(Note.tags))
            .filter(Note.note_id == id)
            .first()
        )
        if note is None:
            return None

        # Свидетельство привязано к дневнику автора. При смене автора
        # перенаправляем заметку в дневник нового автора (создаём, если нет).
        diary = self.db.query(Diary).filter(Diary.author_id == dto.author_id).first()
        if diary is None:
            diary = self.create_diary(
                DiaryDto(
                    author_id=dto.author_id,
                    source="",
                    started_at=dto.created_at,
                    finished_at=dto.created_at,
                )
            )
        note.diary_id = diary.diary_id
        note.created_at = dto.created_at
        note.citation = dto.citation
        note.source = dto.source
        note.localization_accuracy = dto.localization_accuracy
        note.place_type = dto.place_type

        # Тип/темпоральность/теги — перезаписываем целиком новым набором.
        note.note_types = (
            self.db.query(NoteType)
            .filter(NoteType.note_type_id.in_(dto.note_type_ids))
            .all()
        )
        note.temporalities = (
            self.db.query(Temporality)
            .filter(Temporality.temporality_id.in_(dto.temporality_ids))
            .all()
        )
        note.tags = self.db.query(Tag).filter(Tag.tag_id.in_(dto.tag_ids)).all()
        # Новые тегоподобные графы — также перезаписываем целиком.
        note.organizations = (
            self.db.query(Organization)
            .filter(Organization.organization_id.in_(dto.organization_ids))
            .all()
        )
        note.city_names = (
            self.db.query(CityName)
            .filter(CityName.city_name_id.in_(dto.city_name_ids))
            .all()
        )
        note.geo_names = (
            self.db.query(GeoName)
            .filter(GeoName.geo_name_id.in_(dto.geo_name_ids))
            .all()
        )
        note.personalities = (
            self.db.query(Personality)
            .filter(Personality.personality_id.in_(dto.personality_ids))
            .all()
        )

        # Привязки к местам — удаляем старые и кладём новые.
        self.db.query(NoteToPoint).filter(NoteToPoint.note_id == id).delete()
        for ntp in dto.note_to_points:
            self.db.add(
                NoteToPoint(
                    note_id=id,
                    point_id=ntp.point_id,
                    description=ntp.description,
                    latitude=ntp.latitude,
                    longitude=ntp.longitude,
                )
            )

        self.db.commit()
        self.db.refresh(note)
        return note

    def get_note_for_edit(self, id: int):
        """Полный состав свидетельства для предзаполнения формы правки."""
        note = (
            self.db.query(Note)
            .options(
                joinedload(Note.tags),
                joinedload(Note.diary),
                joinedload(Note.note_types),
                joinedload(Note.temporalities),
                joinedload(Note.organizations),
                joinedload(Note.city_names),
                joinedload(Note.geo_names),
                joinedload(Note.personalities),
            )
            .filter(Note.note_id == id)
            .first()
        )
        if note is None:
            return None
        ntps = (
            self.db.query(NoteToPoint).filter(NoteToPoint.note_id == id).all()
        )
        return {
            "note_id": note.note_id,
            "author_id": note.diary.author_id if note.diary else None,
            "note_type_ids": [t.note_type_id for t in note.note_types],
            "temporality_ids": [t.temporality_id for t in note.temporalities],
            "created_at": note.created_at,
            "citation": note.citation,
            "source": note.source,
            "tag_ids": [t.tag_id for t in note.tags],
            "localization_accuracy": note.localization_accuracy,
            "place_type": note.place_type,
            "organization_ids": [o.organization_id for o in note.organizations],
            "city_name_ids": [c.city_name_id for c in note.city_names],
            "geo_name_ids": [g.geo_name_id for g in note.geo_names],
            "personality_ids": [p.personality_id for p in note.personalities],
            "note_to_points": [
                {
                    "point_id": n.point_id,
                    "description": n.description,
                    "latitude": n.latitude,
                    "longitude": n.longitude,
                }
                for n in ntps
            ],
        }

    def delete_note(self, id: int) -> bool:
        note = self.db.query(Note).filter(Note.note_id == id).first()
        if note is None:
            return False
        # Сначала убираем связи (теги, новые графы и привязки к местам),
        # затем само свидетельство.
        self.db.query(NoteToPoint).filter(NoteToPoint.note_id == id).delete()
        self.db.query(NoteToTag).filter(NoteToTag.note_id == id).delete()
        self.db.query(NoteToOrganization).filter(
            NoteToOrganization.note_id == id
        ).delete()
        self.db.query(NoteToCityName).filter(NoteToCityName.note_id == id).delete()
        self.db.query(NoteToGeoName).filter(NoteToGeoName.note_id == id).delete()
        self.db.query(NoteToPersonality).filter(
            NoteToPersonality.note_id == id
        ).delete()
        self.db.delete(note)
        self.db.commit()
        return True

    def create_diary(self, diary: DiaryDto):
        new_diary = Diary(
            author_id=diary.author_id,
            started_at=diary.started_at,
            finished_at=diary.finished_at,
            source=diary.source,
            storage_place=diary.storage_place,
        )
        self.db.add(new_diary)
        self.db.commit()
        self.db.refresh(new_diary)
        return new_diary

    def create_tag(self, dto: TagDto):
        new_tag = Tag(name=dto.name)
        self.db.add(new_tag)
        self.db.commit()
        self.db.refresh(new_tag)
        return new_tag

    def delete_tag(self, id: int):
        """Удаляет тег. None — если тега нет. ValueError — если тег привязан
        хотя бы к одному свидетельству (удаление блокируется).

        Важно: нельзя полагаться на ошибку внешнего ключа — связь note↔tag
        many-to-many, и SQLAlchemy при db.delete(tag) молча удалил бы строки
        note_to_tag. Поэтому проверяем использование явно."""
        tag = self.db.query(Tag).filter(Tag.tag_id == id).first()
        if tag is None:
            return None
        used = self.db.query(NoteToTag).filter(NoteToTag.tag_id == id).count()
        if used > 0:
            raise ValueError(
                f"Тег используется в свидетельствах ({used}). "
                "Сначала снимите его со свидетельств."
            )
        self.db.delete(tag)
        self.db.commit()
        return True

    def delete_taxonomy_if_unused(
        self, model, pk_field: str, join_model, join_fk: str, id: int, label: str
    ):
        """Удаление элемента тегоподобного справочника с проверкой
        использования (как delete_tag). Логика идентична для organization /
        city_name / geo_name / personality, поэтому вынесена в один метод.

        None — элемента нет; ValueError — элемент привязан к свидетельствам."""
        item = self.db.query(model).filter(getattr(model, pk_field) == id).first()
        if item is None:
            return None
        used = (
            self.db.query(join_model)
            .filter(getattr(join_model, join_fk) == id)
            .count()
        )
        if used > 0:
            raise ValueError(
                f"{label} используется в свидетельствах ({used}). "
                "Сначала снимите значение со свидетельств."
            )
        self.db.delete(item)
        self.db.commit()
        return True

    def get_all_diaries(self, filters: DiaryFilterParams | None = None):
        q = self.db.query(Diary).options(joinedload(Diary.author))
        if filters is None:
            return q.all()

        if filters.author_ids:
            q = q.filter(Diary.author_id.in_(filters.author_ids))
        if filters.search:
            pattern = f"%{filters.search}%"
            q = q.filter(Diary.source.ilike(pattern))
        if filters.started_after:
            q = q.filter(Diary.started_at >= filters.started_after)
        if filters.finished_before:
            q = q.filter(Diary.finished_at <= filters.finished_before)
        return q.all()

    def update_diary(self, id: int, dto: DiaryDto):
        diary = self.db.query(Diary).filter(Diary.diary_id == id).first()
        if diary is None:
            return None
        diary.author_id = dto.author_id
        diary.started_at = dto.started_at
        diary.finished_at = dto.finished_at
        diary.source = dto.source
        diary.storage_place = dto.storage_place
        self.db.commit()
        self.db.refresh(diary)
        return diary

    def delete_diary(self, id: int) -> bool:
        diary = self.db.query(Diary).filter(Diary.diary_id == id).first()
        if diary is None:
            return False
        self.db.delete(diary)
        self.db.commit()
        return True

    def get_diary_by_id(self, id: int):
        return (
            self.db.query(Diary)
            .filter(Diary.diary_id == id)
            .options(joinedload(Diary.author))
            .first()
        )

    def get_notes_by_diary(self, diary_id: int, extended: bool):
        query = (
            self.db.query(Note)
            .filter(Note.diary_id == diary_id)
        )
        if extended:
            query = query.options(
                joinedload(Note.temporalities),
                joinedload(Note.tags),
                joinedload(Note.note_types),
                joinedload(Note.points),
            )
        return query.all()
