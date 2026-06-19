from datetime import date
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.authors.models import (
    Card,
    Education,
    FamilyStatus,
    Nationality,
    Occupation,
    PoliticalParty,
    Religion,
    SocialClass,
)
from app.base.utils import check_id_exists_raise


class SexEnum(str, Enum):
    MALE = "M"
    FEMALE = "F"


class AuthorFilterParams(BaseModel):
    search: Optional[str] = None
    sex: Optional[SexEnum] = None
    has_children: Optional[bool] = None
    birth_date_from: Optional[date] = None
    birth_date_to: Optional[date] = None
    family_status_ids: List[int] = []
    social_class_ids: List[int] = []
    nationality_ids: List[int] = []
    religion_ids: List[int] = []
    education_ids: List[int] = []
    occupation_ids: List[int] = []
    political_party_ids: List[int] = []


class AuthorDto(BaseModel):
    # Обязательна только фамилия. Остальное — необязательно.
    last_name: str
    first_name: str | None = None
    middle_name: str | None = None
    sex: SexEnum | None = None
    birth_date: date | None = None  # YYYY-MM-DD
    death_date: date | None = None  # YYYY-MM-DD
    biography: str | None = None
    photo: str | None = None  # data URL (base64)
    has_children: bool | None = None
    family_status_id: int | None = None
    social_class_ids: List[int] = []
    nationality_ids: List[int] = []
    religion_ids: List[int] = []
    education_ids: List[int] = []
    occupation_ids: List[int] = []
    political_party_ids: List[int] = []
    card_ids: List[int] = []

    diary_started_at: date | None = None  # YYYY-MM-DD
    diary_finished_at: date | None = None  # YYYY-MM-DD
    diary_source: str | None = None  # «Публикация дневника»
    diary_storage_place: str | None = None  # «Место хранения дневника»

    def validate_ids(self, db: Session) -> None:
        check_id_exists_raise(db, FamilyStatus, self.family_status_id)
        for id in self.social_class_ids:
            check_id_exists_raise(db, SocialClass, id)
        for id in self.nationality_ids:
            check_id_exists_raise(db, Nationality, id)
        for id in self.religion_ids:
            check_id_exists_raise(db, Religion, id)
        for id in self.education_ids:
            check_id_exists_raise(db, Education, id)
        for id in self.occupation_ids:
            check_id_exists_raise(db, Occupation, id)
        for id in self.political_party_ids:
            check_id_exists_raise(db, PoliticalParty, id)
        for id in self.card_ids:
            check_id_exists_raise(db, Card, id)
