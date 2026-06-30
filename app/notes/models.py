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


# Новые тегоподобные графы (M2M, полностью аналогично note_to_tag).
# Добавлены позже; на существующие данные не влияют — старые свидетельства
# просто не имеют связей в этих таблицах.
class NoteToOrganization(Base):
    __tablename__ = "note_to_organization"
    note_id: Mapped[int] = mapped_column(ForeignKey("note.note_id"), primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organization.organization_id"), primary_key=True
    )


class NoteToCityName(Base):
    __tablename__ = "note_to_city_name"
    note_id: Mapped[int] = mapped_column(ForeignKey("note.note_id"), primary_key=True)
    city_name_id: Mapped[int] = mapped_column(
        ForeignKey("city_name.city_name_id"), primary_key=True
    )


class NoteToGeoName(Base):
    __tablename__ = "note_to_geo_name"
    note_id: Mapped[int] = mapped_column(ForeignKey("note.note_id"), primary_key=True)
    geo_name_id: Mapped[int] = mapped_column(
        ForeignKey("geo_name.geo_name_id"), primary_key=True
    )


class NoteToPersonality(Base):
    __tablename__ = "note_to_personality"
    note_id: Mapped[int] = mapped_column(ForeignKey("note.note_id"), primary_key=True)
    personality_id: Mapped[int] = mapped_column(
        ForeignKey("personality.personality_id"), primary_key=True
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

    # Новые необязательные графы свидетельства (храним, никуда не выводим):
    #   localization_accuracy — «Точность локализации» («Эллипсис»/«Точное место»);
    #   place_type — «Тип места» (место жительства/работы/… или «Другое»).
    # Nullable: у уже заведённых свидетельств остаются NULL.
    localization_accuracy: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    place_type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

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
    # Новые тегоподобные графы.
    organizations: Mapped[List["Organization"]] = relationship(
        secondary=NoteToOrganization.__tablename__, back_populates="notes"
    )
    city_names: Mapped[List["CityName"]] = relationship(
        secondary=NoteToCityName.__tablename__, back_populates="notes"
    )
    geo_names: Mapped[List["GeoName"]] = relationship(
        secondary=NoteToGeoName.__tablename__, back_populates="notes"
    )
    personalities: Mapped[List["Personality"]] = relationship(
        secondary=NoteToPersonality.__tablename__, back_populates="notes"
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


# Новые справочники (id + name), полностью аналогичны Tag.
class Organization(ExtendedBaseClass):
    __tablename__ = "organization"
    organization_id: Mapped[intpk]
    notes: Mapped[List["Note"]] = relationship(
        secondary=NoteToOrganization.__tablename__, back_populates="organizations"
    )


class CityName(ExtendedBaseClass):
    __tablename__ = "city_name"
    city_name_id: Mapped[intpk]
    notes: Mapped[List["Note"]] = relationship(
        secondary=NoteToCityName.__tablename__, back_populates="city_names"
    )


class GeoName(ExtendedBaseClass):
    __tablename__ = "geo_name"
    geo_name_id: Mapped[intpk]
    notes: Mapped[List["Note"]] = relationship(
        secondary=NoteToGeoName.__tablename__, back_populates="geo_names"
    )


class Personality(ExtendedBaseClass):
    __tablename__ = "personality"
    personality_id: Mapped[intpk]
    notes: Mapped[List["Note"]] = relationship(
        secondary=NoteToPersonality.__tablename__, back_populates="personalities"
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
