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
from app.notes.models import Diary, Note
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

    @staticmethod
    def _serialize_author_list(author: Author) -> dict:
        """Плоский формат автора с атрибутами — для фильтрации на клиенте."""

        def items(rows, id_attr):
            return [{"id": getattr(r, id_attr), "name": r.name} for r in rows]

        return {
            "author_id": author.author_id,
            "first_name": author.first_name,
            "middle_name": author.middle_name,
            "last_name": author.last_name,
            "sex": author.sex,
            "birth_date": author.birth_date,
            "death_date": author.death_date,
            "biography": author.biography,
            "photo": author.photo,
            "has_children": author.has_children,
            "family_status_id": author.family_status_id,
            "family_status": (
                {
                    "id": author.family_status.family_status_id,
                    "name": author.family_status.name,
                }
                if author.family_status
                else None
            ),
            "social_classes": items(author.social_classes, "social_class_id"),
            "nationalities": items(author.nationalities, "nationality_id"),
            "religions": items(author.religions, "religion_id"),
            "education": items(author.education, "education_id"),
            "occupation": items(author.occupation, "occupation_id"),
            "political_parties": items(
                author.political_parties, "political_party_id"
            ),
            "cards": items(author.cards, "card_id"),
        }

    def get_all(self, filters: AuthorFilterParams | None = None):
        q = self.db.query(Author).options(
            joinedload(Author.family_status),
            joinedload(Author.social_classes),
            joinedload(Author.nationalities),
            joinedload(Author.religions),
            joinedload(Author.education),
            joinedload(Author.occupation),
            joinedload(Author.political_parties),
            joinedload(Author.cards),
        )
        if filters is None:
            return [self._serialize_author_list(a) for a in q.all()]

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
        if filters.birth_date_from:
            q = q.filter(Author.birth_date >= filters.birth_date_from)
        if filters.birth_date_to:
            q = q.filter(Author.birth_date <= filters.birth_date_to)
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

        return [self._serialize_author_list(a) for a in q.distinct().all()]

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
                death_date=dto.death_date,
                biography=dto.biography,
                photo=dto.photo,
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
                    storage_place=dto.diary_storage_place,
                    started_at=dto.diary_started_at,
                    finished_at=dto.diary_finished_at,
                )
            )

            self.db.refresh(author)
            return {"author": author, "diary": diary}
        except IntegrityError as e:
            raise Exception(str(e.orig))

    def update(self, id: int, dto: AuthorDto):
        author = (
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
        if author is None:
            return None

        try:
            author.last_name = dto.last_name
            author.first_name = dto.first_name
            author.middle_name = dto.middle_name
            author.sex = dto.sex
            author.birth_date = dto.birth_date
            author.death_date = dto.death_date
            author.biography = dto.biography
            author.photo = dto.photo
            author.has_children = dto.has_children
            author.family_status_id = dto.family_status_id

            # Связи many-to-many перезаписываем целиком новым набором.
            author.social_classes = (
                self.db.query(SocialClass)
                .filter(SocialClass.social_class_id.in_(dto.social_class_ids))
                .all()
            )
            author.nationalities = (
                self.db.query(Nationality)
                .filter(Nationality.nationality_id.in_(dto.nationality_ids))
                .all()
            )
            author.religions = (
                self.db.query(Religion)
                .filter(Religion.religion_id.in_(dto.religion_ids))
                .all()
            )
            author.education = (
                self.db.query(Education)
                .filter(Education.education_id.in_(dto.education_ids))
                .all()
            )
            author.occupation = (
                self.db.query(Occupation)
                .filter(Occupation.occupation_id.in_(dto.occupation_ids))
                .all()
            )
            author.political_parties = (
                self.db.query(PoliticalParty)
                .filter(PoliticalParty.political_party_id.in_(dto.political_party_ids))
                .all()
            )
            author.cards = (
                self.db.query(Card).filter(Card.card_id.in_(dto.card_ids)).all()
            )

            self.db.commit()

            # Обновляем дневник автора (или создаём, если его ещё нет).
            diary = (
                self.db.query(Diary)
                .filter(Diary.author_id == id)
                .order_by(Diary.diary_id)
                .first()
            )
            if diary is None:
                note_service = NoteService(self.db)
                diary = note_service.create_diary(
                    DiaryDto(
                        author_id=id,
                        source=dto.diary_source,
                        storage_place=dto.diary_storage_place,
                        started_at=dto.diary_started_at,
                        finished_at=dto.diary_finished_at,
                    )
                )
            else:
                diary.started_at = dto.diary_started_at
                diary.finished_at = dto.diary_finished_at
                diary.source = dto.diary_source
                diary.storage_place = dto.diary_storage_place
                self.db.commit()

            self.db.refresh(author)
            return {"author": author, "diary": diary}
        except IntegrityError as e:
            self.db.rollback()
            raise Exception(str(e.orig))

    def delete_author(self, id: int):
        """Удаляет автора. Возвращает None, если автора нет. Бросает ValueError,
        если у автора есть свидетельства (удаление блокируется)."""
        author = self.db.query(Author).filter(Author.author_id == id).first()
        if author is None:
            return None

        note_count = (
            self.db.query(Note)
            .join(Diary, Note.diary_id == Diary.diary_id)
            .filter(Diary.author_id == id)
            .count()
        )
        if note_count > 0:
            raise ValueError(
                f"У автора есть свидетельства ({note_count}). "
                "Сначала удалите или перепривяжите их."
            )

        # Чистим связи many-to-many и пустые дневники, затем самого автора.
        author.social_classes = []
        author.nationalities = []
        author.religions = []
        author.education = []
        author.occupation = []
        author.political_parties = []
        author.cards = []
        author.points = []
        self.db.commit()

        self.db.query(Diary).filter(Diary.author_id == id).delete()
        self.db.delete(author)
        self.db.commit()
        return True
