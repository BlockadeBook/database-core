import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base.models import *

if TYPE_CHECKING:
    from app.authors.models import Author
    from app.point.models import Point


class NoteToTag(Base):
    __tablename__ = "note_to_tag"
    note_id: Mapped[int] = mapped_column(ForeignKey("note.note_id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tag.tag_id"), primary_key=True)


class NoteToNoteType(Base):
    __tablename__ = "note_to_note_type"
    note_id: Mapped[int] = mapped_column(ForeignKey("note.note_id"), primary_key=True)
    note_type_id: Mapped[int] = mapped_column(
        ForeignKey("note_type.note_type_id"), primary_key=True
    )


class NoteToTemporality(Base):
    __tablename__ = "note_to_temporality"
    note_id: Mapped[int] = mapped_column(ForeignKey("note.note_id"), primary_key=True)
    temporality_id: Mapped[int] = mapped_column(
        ForeignKey("temporality.temporality_id"), primary_key=True
    )


class NoteToPoint(Base):
    __tablename__ = "note_to_point"
    note_id: Mapped[int] = mapped_column(ForeignKey("note.note_id"), primary_key=True)
    point_id: Mapped[int] = mapped_column(
        ForeignKey("point.point_id"), primary_key=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    # Координаты конкретного свидетельства для мест без фиксированной
    # координаты (кладбище, улица/площадь и т.п.). Для мест с фиксированной
    # координатой остаются NULL — координата берётся из point_coordinates.
    latitude: Mapped[Optional[float]] = mapped_column(nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(nullable=True)


class Note(Base):
    __tablename__ = "note"
    note_id: Mapped[intpk]
    diary_id: Mapped[int] = mapped_column(ForeignKey("diary.diary_id"))
    created_at: Mapped[datetime.date] = mapped_column(nullable=False)
    citation: Mapped[str] = mapped_column(Text, nullable=False)
    # Text (без лимита), т.к. источник — полная библиографическая ссылка
    # (как и diary.source). VARCHAR(63) обрезал длинные ссылки при сохранении.
    source: Mapped[str] = mapped_column(Text, nullable=False)

    # Тип свидетельства и темпоральность — множественный выбор (M2M, как теги).
    note_types: Mapped[List["NoteType"]] = relationship(
        secondary=NoteToNoteType.__tablename__, back_populates="notes"
    )
    temporalities: Mapped[List["Temporality"]] = relationship(
        secondary=NoteToTemporality.__tablename__, back_populates="notes"
    )
    diary: Mapped["Diary"] = relationship(back_populates="notes")
    tags: Mapped[List["Tag"]] = relationship(
        secondary=NoteToTag.__tablename__, back_populates="notes"
    )
    points: Mapped[List["Point"]] = relationship(
        secondary=NoteToPoint.__tablename__, back_populates="notes"
    )


class Diary(Base):
    __tablename__ = "diary"
    diary_id: Mapped[intpk]
    author_id: Mapped[int] = mapped_column(ForeignKey("author.author_id"))
    started_at: Mapped[datetime.date] = mapped_column(nullable=True)
    finished_at: Mapped[datetime.date] = mapped_column(nullable=True)
    # source — «Публикация дневника»; storage_place — «Место хранения дневника»
    source: Mapped[str] = mapped_column(Text, nullable=True)
    storage_place: Mapped[str] = mapped_column(Text, nullable=True)

    author: Mapped["Author"] = relationship(back_populates="diaries")
    notes: Mapped[List["Note"]] = relationship(back_populates="diary")


class Tag(ExtendedBaseClass):
    __tablename__ = "tag"
    tag_id: Mapped[intpk]
    notes: Mapped[List["Note"]] = relationship(
        secondary=NoteToTag.__tablename__, back_populates="tags"
    )


class NoteType(ExtendedBaseClass):
    __tablename__ = "note_type"
    note_type_id: Mapped[intpk]
    notes: Mapped[List["Note"]] = relationship(
        secondary=NoteToNoteType.__tablename__, back_populates="note_types"
    )


class Temporality(ExtendedBaseClass):
    __tablename__ = "temporality"
    temporality_id: Mapped[intpk]
    notes: Mapped[List["Note"]] = relationship(
        secondary=NoteToTemporality.__tablename__, back_populates="temporalities"
    )


def init():
    # заглушка
    # не убирайте пжпж
    pass
