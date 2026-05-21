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
    Diary,
    Note,
    NoteToPoint,
    NoteToTag,
    NoteType,
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
        }

    def get_all(self, filters: NoteFilterParams | None = None):
        q = self.db.query(Note)
        if filters is None:
            return q.all()

        if filters.search:
            pattern = f"%{filters.search}%"
            q = q.filter(
                or_(Note.citation.ilike(pattern), Note.source.ilike(pattern))
            )
        if filters.note_type_ids:
            q = q.filter(Note.note_type_id.in_(filters.note_type_ids))
        if filters.temporality_ids:
            q = q.filter(Note.temporality_id.in_(filters.temporality_ids))
        if filters.diary_ids:
            q = q.filter(Note.diary_id.in_(filters.diary_ids))
        if filters.author_ids:
            q = q.join(Diary, Note.diary_id == Diary.diary_id).filter(
                Diary.author_id.in_(filters.author_ids)
            )
        if filters.tag_ids:
            q = q.join(NoteToTag).filter(NoteToTag.tag_id.in_(filters.tag_ids))
        if filters.point_ids:
            q = q.join(NoteToPoint).filter(NoteToPoint.point_id.in_(filters.point_ids))
        if filters.date_from:
            q = q.filter(Note.created_at >= filters.date_from)
        if filters.date_to:
            q = q.filter(Note.created_at <= filters.date_to)
        return q.distinct().all()

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
                joinedload(Note.temporality),
                joinedload(Note.tags),
                joinedload(Note.note_type),
            )
            .first()
            ._asdict()  # type: ignore
        )

    def get_detailed_by_id(self, id: int):
        # выглядит страшно, но какое тз такое хз
        res = (self.db.query(
            Note,
            Author
        ).join(Diary, Diary.diary_id == Note.diary_id)
               .join(Author, Author.author_id == Diary.author_id)
               .options(joinedload(Note.note_type))
               .options(joinedload(Note.tags))
               .options(joinedload(Author.education))
               .options(joinedload(Author.family_status))
               .options(joinedload(Note.points).joinedload(Point.point_coordinates))
               .filter(Note.note_id == id).first())
        res = res._asdict()
        return res

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
            note_type_id=dto.note_type_id,
            temporality_id=dto.temporality_id,
            created_at=dto.created_at,
            citation=dto.citation,
            source=dto.source,
        )
        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)

        for ntp in dto.note_to_points:
            self.db.add(
                NoteToPoint(
                    note_id=note.note_id,
                    point_id=ntp.point_id,
                    description=ntp.description,
                )
            )

        note.tags.extend(self.db.query(Tag).filter(Tag.tag_id.in_(dto.tag_ids)).all())

        self.db.commit()
        self.db.refresh(note)
        return note

    def create_diary(self, diary: DiaryDto):
        new_diary = Diary(
            author_id=diary.author_id,
            started_at=diary.started_at,
            finished_at=diary.finished_at,
            source=diary.source,
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
                joinedload(Note.temporality),
                joinedload(Note.tags),
                joinedload(Note.note_type),
                joinedload(Note.points),
            )
        return query.all()
