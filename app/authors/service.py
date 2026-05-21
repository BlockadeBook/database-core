from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.authors.dtos import AuthorDto, AuthorFilterParams
from app.authors.models import (
    Author,
    AuthorToEducation,
    AuthorToNationality,
    AuthorToOccupation,
    AuthorToPoliticalParty,
    AuthorToReligion,
    AuthorToSocialClass,
    Card,
    Education,
    FamilyStatus,
    Nationality,
    Occupation,
    PoliticalParty,
    Religion,
    SocialClass,
)
from app.notes.dtos import DiaryDto
from app.notes.service import NoteService


class AuthorService:
    db: Session

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_filters(self):
        return {
            "family_statuses": self.db.query(FamilyStatus).all(),
            "social_classes": self.db.query(SocialClass).all(),
            "nationalities": self.db.query(Nationality).all(),
            "religions": self.db.query(Religion).all(),
            "educations": self.db.query(Education).all(),
            "occupations": self.db.query(Occupation).all(),
            "political_parties": self.db.query(PoliticalParty).all(),
            "cards": self.db.query(Card).all(),
        }

    def get_all(self, filters: AuthorFilterParams | None = None):
        q = self.db.query(Author)
        if filters is None:
            return q.all()

        if filters.search:
            pattern = f"%{filters.search}%"
            q = q.filter(
                or_(
                    Author.first_name.ilike(pattern),
                    Author.middle_name.ilike(pattern),
                    Author.last_name.ilike(pattern),
                )
            )
        if filters.sex:
            q = q.filter(Author.sex == filters.sex)
        if filters.has_children is not None:
            q = q.filter(Author.has_children == filters.has_children)
        if filters.family_status_ids:
            q = q.filter(Author.family_status_id.in_(filters.family_status_ids))
        if filters.social_class_ids:
            q = q.join(AuthorToSocialClass).filter(
                AuthorToSocialClass.social_class_id.in_(filters.social_class_ids)
            )
        if filters.nationality_ids:
            q = q.join(AuthorToNationality).filter(
                AuthorToNationality.nationality_id.in_(filters.nationality_ids)
            )
        if filters.religion_ids:
            q = q.join(AuthorToReligion).filter(
                AuthorToReligion.religion_id.in_(filters.religion_ids)
            )
        if filters.education_ids:
            q = q.join(AuthorToEducation).filter(
                AuthorToEducation.education_id.in_(filters.education_ids)
            )
        if filters.occupation_ids:
            q = q.join(AuthorToOccupation).filter(
                AuthorToOccupation.occupation_id.in_(filters.occupation_ids)
            )
        if filters.political_party_ids:
            q = q.join(AuthorToPoliticalParty).filter(
                AuthorToPoliticalParty.political_party_id.in_(filters.political_party_ids)
            )

        return q.distinct().all()

    def get_by_id(self, id: int, extended: bool):
        if not extended:
            return (
                self.db.query(
                    Author.author_id,
                    Author.first_name,
                    Author.middle_name,
                    Author.last_name,
                )
                .filter(Author.author_id == id)
                .first()
                ._asdict()  # type: ignore
            )

        return (
            self.db.query(Author)
            .filter(Author.author_id == id)
            .options(
                joinedload(Author.social_classes),
                joinedload(Author.nationalities),
                joinedload(Author.religions),
                joinedload(Author.education),
                joinedload(Author.occupation),
                joinedload(Author.political_parties),
                joinedload(Author.cards),
            )
            .first()
        )

    def create(self, dto: AuthorDto):
        try:
            author = Author(
                last_name=dto.last_name,
                first_name=dto.first_name,
                middle_name=dto.middle_name,
                sex=dto.sex,
                birth_date=dto.birth_date,
                biography=dto.biography,
                has_children=dto.has_children,
                family_status=self.db.query(FamilyStatus)
                .filter(FamilyStatus.family_status_id == dto.family_status_id)
                .first(),
            )
            self.db.add(author)
            self.db.commit()
            self.db.refresh(author)

            author.social_classes.extend(
                self.db.query(SocialClass)
                .filter(SocialClass.social_class_id.in_(dto.social_class_ids))
                .all()
            )
            author.nationalities.extend(
                self.db.query(Nationality)
                .filter(Nationality.nationality_id.in_(dto.nationality_ids))
                .all()
            )
            author.religions.extend(
                self.db.query(Religion)
                .filter(Religion.religion_id.in_(dto.religion_ids))
                .all()
            )
            author.education.extend(
                self.db.query(Education)
                .filter(Education.education_id.in_(dto.education_ids))
                .all()
            )
            author.occupation.extend(
                self.db.query(Occupation)
                .filter(Occupation.occupation_id.in_(dto.occupation_ids))
                .all()
            )
            author.political_parties.extend(
                self.db.query(PoliticalParty)
                .filter(PoliticalParty.political_party_id.in_(dto.political_party_ids))
                .all()
            )
            author.cards.extend(
                self.db.query(Card).filter(Card.card_id.in_(dto.card_ids)).all()
            )

            self.db.commit()

            # create a diary object for this author
            note_service = NoteService(self.db)
            diary = note_service.create_diary(
                DiaryDto(
                    author_id=author.author_id,
                    source=dto.diary_source,
                    started_at=dto.diary_started_at,
                    finished_at=dto.diary_finished_at,
                )
            )

            self.db.refresh(author)
            return {"author": author, "diary": diary}
        except IntegrityError as e:
            raise Exception(str(e.orig))
