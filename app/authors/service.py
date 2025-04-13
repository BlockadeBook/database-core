from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.authors.dtos import AuthorDto
from app.authors.models import (
    Author,
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

    def get_all(self):
        return self.db.query(Author).all()

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
