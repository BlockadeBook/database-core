from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.authors.dtos import AuthorDto, AuthorFilterParams, SexEnum
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
from app.authors.service import AuthorService
from app.base.query_params import parse_int_csv
from app.base.taxonomy import make_named_taxonomy_router
from app.database import get_db

router = APIRouter(prefix="/authors")


@router.get("/filters")
def get_filters(db: Session = Depends(get_db)):
    author_service = AuthorService(db)
    return author_service.get_filters()


@router.get("/")
def get_all(
    search: Optional[str] = None,
    sex: Optional[SexEnum] = None,
    has_children: Optional[bool] = None,
    birth_date_from: Optional[date] = None,
    birth_date_to: Optional[date] = None,
    family_status_ids: Optional[str] = None,
    social_class_ids: Optional[str] = None,
    nationality_ids: Optional[str] = None,
    religion_ids: Optional[str] = None,
    education_ids: Optional[str] = None,
    occupation_ids: Optional[str] = None,
    political_party_ids: Optional[str] = None,
    db: Session = Depends(get_db),
):
    filters = AuthorFilterParams(
        search=search,
        sex=sex,
        has_children=has_children,
        birth_date_from=birth_date_from,
        birth_date_to=birth_date_to,
        family_status_ids=parse_int_csv(family_status_ids),
        social_class_ids=parse_int_csv(social_class_ids),
        nationality_ids=parse_int_csv(nationality_ids),
        religion_ids=parse_int_csv(religion_ids),
        education_ids=parse_int_csv(education_ids),
        occupation_ids=parse_int_csv(occupation_ids),
        political_party_ids=parse_int_csv(political_party_ids),
    )
    author_service = AuthorService(db)
    return author_service.get_all(filters)


@router.get("/{id}")
def get_one(id: int, extended: bool = True, db: Session = Depends(get_db)):
    author_service = AuthorService(db)
    res = author_service.get_by_id(id, extended)
    if res is None:
        raise HTTPException(404)
    return res


@router.post("/")
async def create(author: AuthorDto, db: Session = Depends(get_db)):
    author.validate_ids(db)
    author_service = AuthorService(db)
    try:
        created_author = author_service.create(author)
        return created_author
    except Exception as e:
        raise HTTPException(400, str(e))


@router.patch("/{id}")
async def update(id: int, author: AuthorDto, db: Session = Depends(get_db)):
    author.validate_ids(db)
    author_service = AuthorService(db)
    try:
        res = author_service.update(id, author)
    except Exception as e:
        raise HTTPException(400, str(e))
    if res is None:
        raise HTTPException(404)
    return res


@router.delete("/{id}", status_code=204)
async def delete(id: int, db: Session = Depends(get_db)):
    author_service = AuthorService(db)
    try:
        res = author_service.delete_author(id)
    except ValueError as e:
        raise HTTPException(409, str(e))
    if res is None:
        raise HTTPException(404)


# Taxonomies — simple name-only entities
router.include_router(
    make_named_taxonomy_router(FamilyStatus, "family_status_id"),
    prefix="/family-statuses",
)
router.include_router(
    make_named_taxonomy_router(SocialClass, "social_class_id"),
    prefix="/social-classes",
)
router.include_router(
    make_named_taxonomy_router(Nationality, "nationality_id"),
    prefix="/nationalities",
)
router.include_router(
    make_named_taxonomy_router(Religion, "religion_id"),
    prefix="/religions",
)
router.include_router(
    make_named_taxonomy_router(Education, "education_id"),
    prefix="/educations",
)
router.include_router(
    make_named_taxonomy_router(Occupation, "occupation_id"),
    prefix="/occupations",
)
router.include_router(
    make_named_taxonomy_router(PoliticalParty, "political_party_id"),
    prefix="/political-parties",
)
router.include_router(
    make_named_taxonomy_router(Card, "card_id"),
    prefix="/cards",
)
