from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.authors.models import AuthorToPoint
from app.base.models import *
from app.notes.models import NoteToPoint

if TYPE_CHECKING:
    from app.authors.models import Author
    from app.notes.models import Note


class Rayon(ExtendedBaseClass):
    __tablename__ = "rayon"
    rayon_id: Mapped[intpk]
    points: Mapped[List["Point"]] = relationship(back_populates="rayon")


class PointType(ExtendedBaseClass):
    __tablename__ = "point_type"
    point_type_id: Mapped[intpk]
    has_fixed_coordinates: Mapped[bool] = mapped_column(nullable=False)
    has_address: Mapped[bool] = mapped_column(nullable=False)
    points: Mapped[List["Point"]] = relationship(back_populates="point_type")
    point_subtypes: Mapped[List["PointSubType"]] = relationship(
        back_populates="point_type"
    )


class PointSubType(ExtendedBaseClass):
    __tablename__ = "point_subtype"
    point_subtype_id: Mapped[intpk]
    point_type_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("point_type.point_type_id")
    )
    point_type: Mapped[Optional["PointType"]] = relationship(
        back_populates="point_subtypes"
    )

    points: Mapped[List["Point"]] = relationship(back_populates="point_subtype")
    point_subsubtypes: Mapped[List["PointSubSubType"]] = relationship(
        back_populates="point_subtype"
    )


class PointSubSubType(ExtendedBaseClass):
    __tablename__ = "point_subsubtype"
    point_subsubtype_id: Mapped[intpk]
    point_subtype_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("point_subtype.point_subtype_id")
    )
    point_subtype: Mapped[Optional["PointSubType"]] = relationship(
        back_populates="point_subsubtypes"
    )
    points: Mapped[List["Point"]] = relationship(back_populates="point_subsubtype")


class Point(ExtendedBaseClass):
    __tablename__ = "point"
    point_id: Mapped[intpk]
    rayon_id: Mapped[int] = mapped_column(ForeignKey("rayon.rayon_id"))
    street: Mapped[str] = mapped_column(VARCHAR(31))
    building: Mapped[str] = mapped_column(VARCHAR(15))
    point_type_id: Mapped[int] = mapped_column(
        ForeignKey("point_type.point_type_id"), nullable=False
    )
    point_subtype_id: Mapped[int] = mapped_column(
        ForeignKey("point_subtype.point_subtype_id"), nullable=True
    )
    point_subsubtype_id: Mapped[int] = mapped_column(
        ForeignKey("point_subsubtype.point_subsubtype_id"), nullable=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=True)

    rayon: Mapped["Rayon"] = relationship(back_populates="points")
    point_type: Mapped["PointType"] = relationship(back_populates="points")
    point_subtype: Mapped["PointSubType"] = relationship(back_populates="points")
    point_subsubtype: Mapped["PointSubSubType"] = relationship(back_populates="points")
    notes: Mapped[List["Note"]] = relationship(
        secondary=NoteToPoint.__tablename__, back_populates="points"
    )
    authors: Mapped["Author"] = relationship(
        secondary=AuthorToPoint.__tablename__, back_populates="points"
    )
    point_coordinates: Mapped[List["PointCoordinates"]] = relationship(
        back_populates="points"
    )


class PointCoordinates(Base):
    __tablename__ = "point_coordinates"
    point_id: Mapped[int] = mapped_column(
        ForeignKey("point.point_id"), primary_key=True
    )
    latitude: Mapped[float] = mapped_column(nullable=False, primary_key=True)
    longitude: Mapped[float] = mapped_column(nullable=False, primary_key=True)
    points: Mapped["Point"] = relationship(back_populates="point_coordinates")


def init():
    # заглушка
    # не убирайте пжпж
    pass
