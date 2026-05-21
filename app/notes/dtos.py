from datetime import date
from typing import List, Optional

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.authors.models import Author
from app.base.utils import check_id_exists_raise
from app.notes.models import NoteType, Tag, Temporality
from app.point.models import Point


class DiaryDto(BaseModel):
    # TODO: validate dates (min and max)
    started_at: date  # YYYY-MM-DD
    finished_at: date  # YYYY-MM-DD
    source: str
    author_id: int


class Note2PointDto(BaseModel):
    point_id: int
    description: str

    def validate_ids(self, db: Session):
        check_id_exists_raise(db, Point, self.point_id)


class NoteDto(BaseModel):
    author_id: int
    note_type_id: int
    temporality_id: int
    created_at: date  # YYYY-MM-DD
    citation: str
    source: str
    tag_ids: List[int]
    note_to_points: List[Note2PointDto]

    def validate_ids(self, db: Session):
        check_id_exists_raise(db, Author, self.author_id)
        check_id_exists_raise(db, NoteType, self.note_type_id)
        check_id_exists_raise(db, Temporality, self.temporality_id)
        for tag_id in self.tag_ids:
            check_id_exists_raise(db, Tag, tag_id)
        for note_to_point in self.note_to_points:
            note_to_point.validate_ids(db)


class TagDto(BaseModel):
    name: str


class NoteFilterParams(BaseModel):
    search: Optional[str] = None
    note_type_ids: List[int] = []
    temporality_ids: List[int] = []
    diary_ids: List[int] = []
    author_ids: List[int] = []
    tag_ids: List[int] = []
    point_ids: List[int] = []
    date_from: Optional[date] = None
    date_to: Optional[date] = None


class DiaryFilterParams(BaseModel):
    author_ids: List[int] = []
    search: Optional[str] = None
    started_after: Optional[date] = None
    finished_before: Optional[date] = None
