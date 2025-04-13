from sqlalchemy.orm import Session, joinedload

from app.authors.models import Author
from app.notes.dtos import DiaryDto, NoteDto, TagDto
from app.notes.models import Diary, Note, NoteToPoint, NoteType, Tag, Temporality


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

    def get_all(self):
        return self.db.query(Note).all()

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
