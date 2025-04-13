import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base.models import *

if TYPE_CHECKING:
    from app.notes.models import Diary
    from app.point.models import Point


class AuthorToPoliticalParty(Base):
    __tablename__ = "author_to_political_party"
    author_id: Mapped[int] = mapped_column(
        ForeignKey("author.author_id"), primary_key=True
    )
    political_party_id: Mapped[int] = mapped_column(
        ForeignKey("political_party.political_party_id"), primary_key=True
    )


class AuthorToReligion(Base):
    __tablename__ = "author_to_religion"
    author_id: Mapped[int] = mapped_column(
        ForeignKey("author.author_id"), primary_key=True
    )
    religion_id: Mapped[int] = mapped_column(
        ForeignKey("religion.religion_id"), primary_key=True
    )


class AuthorToSocialClass(Base):
    __tablename__ = "author_to_social_class"
    author_id: Mapped[int] = mapped_column(
        ForeignKey("author.author_id"), primary_key=True
    )
    social_class_id: Mapped[int] = mapped_column(
        ForeignKey("social_class.social_class_id"), primary_key=True
    )


class AuthorToNationality(Base):
    __tablename__ = "author_to_nationality"
    author_id: Mapped[int] = mapped_column(
        ForeignKey("author.author_id"), primary_key=True
    )
    nationality_id: Mapped[int] = mapped_column(
        ForeignKey("nationality.nationality_id"), primary_key=True
    )


class AuthorToEducation(Base):
    __tablename__ = "author_to_education"
    author_id: Mapped[int] = mapped_column(
        ForeignKey("author.author_id"), primary_key=True
    )
    education_id: Mapped[int] = mapped_column(
        ForeignKey("education.education_id"), primary_key=True
    )


class AuthorToOccupation(Base):
    __tablename__ = "author_to_occupation"
    author_id: Mapped[int] = mapped_column(
        ForeignKey("author.author_id"), primary_key=True
    )
    occupation_id: Mapped[int] = mapped_column(
        ForeignKey("occupation.occupation_id"), primary_key=True
    )


class AuthorToCard(Base):
    __tablename__ = "author_to_card"
    author_id: Mapped[int] = mapped_column(
        ForeignKey("author.author_id"), primary_key=True
    )
    card_id: Mapped[int] = mapped_column(ForeignKey("card.card_id"), primary_key=True)


class AuthorToPoint(Base):
    __tablename__ = "author_to_point"
    author_id: Mapped[int] = mapped_column(
        ForeignKey("author.author_id"), primary_key=True
    )
    point_id: Mapped[int] = mapped_column(
        ForeignKey("point.point_id"), primary_key=True
    )
    from_date: Mapped[Date] = mapped_column(Date, nullable=False)
    to_date: Mapped[Date] = mapped_column(Date, nullable=False)
    description: Mapped[Text] = mapped_column(Text, nullable=False)


class Author(Base):
    __tablename__ = "author"
    author_id: Mapped[intpk]
    first_name: Mapped[namestr]
    middle_name: Mapped[namestr] = mapped_column(nullable=True)
    last_name: Mapped[namestr]
    sex: Mapped[str] = mapped_column(String(1), nullable=False)
    birth_date: Mapped[datetime.date] = mapped_column(nullable=False)
    family_status_id: Mapped[int] = mapped_column(
        ForeignKey("family_status.family_status_id")
    )
    has_children: Mapped[bool] = mapped_column(nullable=False)
    biography: Mapped[str] = mapped_column(Text, nullable=False, unique=True)

    family_status: Mapped["FamilyStatus"] = relationship(back_populates="authors")
    diaries: Mapped[List["Diary"]] = relationship(back_populates="author")
    political_parties: Mapped[List["PoliticalParty"]] = relationship(
        secondary=AuthorToPoliticalParty.__tablename__, back_populates="authors"
    )
    religions: Mapped[List["Religion"]] = relationship(
        secondary=AuthorToReligion.__tablename__, back_populates="authors"
    )
    social_classes: Mapped[List["SocialClass"]] = relationship(
        secondary=AuthorToSocialClass.__tablename__, back_populates="authors"
    )
    nationalities: Mapped[List["Nationality"]] = relationship(
        secondary=AuthorToNationality.__tablename__, back_populates="authors"
    )
    education: Mapped[List["Education"]] = relationship(
        secondary=AuthorToEducation.__tablename__, back_populates="authors"
    )
    occupation: Mapped[List["Occupation"]] = relationship(
        secondary=AuthorToOccupation.__tablename__, back_populates="authors"
    )
    cards: Mapped[List["Card"]] = relationship(
        secondary=AuthorToCard.__tablename__, back_populates="authors"
    )
    points: Mapped[List["Point"]] = relationship(
        secondary=AuthorToPoint.__tablename__, back_populates="authors"
    )


class FamilyStatus(ExtendedBaseClass):
    __tablename__ = "family_status"
    family_status_id: Mapped[intpk]
    authors: Mapped[List["Author"]] = relationship(back_populates="family_status")


class PoliticalParty(ExtendedBaseClass):
    __tablename__ = "political_party"
    political_party_id: Mapped[intpk]
    authors: Mapped[List["Author"]] = relationship(
        secondary=AuthorToPoliticalParty.__tablename__,
        back_populates="political_parties",
    )


class Religion(ExtendedBaseClass):
    __tablename__ = "religion"
    religion_id: Mapped[intpk]
    authors: Mapped[List["Author"]] = relationship(
        secondary=AuthorToReligion.__tablename__, back_populates="religions"
    )


class SocialClass(ExtendedBaseClass):
    __tablename__ = "social_class"
    social_class_id: Mapped[intpk]
    authors: Mapped[List["Author"]] = relationship(
        secondary=AuthorToSocialClass.__tablename__, back_populates="social_classes"
    )


class Nationality(ExtendedBaseClass):
    __tablename__ = "nationality"
    nationality_id: Mapped[intpk]
    authors: Mapped[List["Author"]] = relationship(
        secondary=AuthorToNationality.__tablename__, back_populates="nationalities"
    )


class Education(ExtendedBaseClass):
    __tablename__ = "education"
    education_id: Mapped[intpk]
    authors: Mapped[List["Author"]] = relationship(
        secondary=AuthorToEducation.__tablename__, back_populates="education"
    )


class Occupation(ExtendedBaseClass):
    __tablename__ = "occupation"
    occupation_id: Mapped[intpk]
    authors: Mapped[List["Author"]] = relationship(
        secondary=AuthorToOccupation.__tablename__, back_populates="occupation"
    )


class Card(ExtendedBaseClass):
    __tablename__ = "card"
    card_id: Mapped[intpk]
    authors: Mapped[List["Author"]] = relationship(
        secondary=AuthorToCard.__tablename__, back_populates="cards"
    )


def init():
    # заглушка
    # не убирайте пжпж
    pass
