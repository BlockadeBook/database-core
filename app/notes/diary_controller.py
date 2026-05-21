from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.base.query_params import parse_int_csv
from app.base.utils import check_id_exists_raise
from app.authors.models import Author
from app.database import get_db
from app.notes.dtos import DiaryDto, DiaryFilterParams
from app.notes.service import NoteService

router = APIRouter(prefix="/diaries")


@router.get("/")
def get_all(
    author_ids: Optional[str] = None,
    search: Optional[str] = None,
    started_after: Optional[date] = None,
    finished_before: Optional[date] = None,
    db: Session = Depends(get_db),
):
    filters = DiaryFilterParams(
        author_ids=parse_int_csv(author_ids),
        search=search,
        started_after=started_after,
        finished_before=finished_before,
    )
    service = NoteService(db)
    return service.get_all_diaries(filters)


@router.get("/{id}")
def get_one(id: int, db: Session = Depends(get_db)):
    service = NoteService(db)
    res = service.get_diary_by_id(id)
    if res is None:
        raise HTTPException(404)
    return res


@router.get("/{id}/notes")
def get_notes(id: int, extended: bool = True, db: Session = Depends(get_db)):
    service = NoteService(db)
    res = service.get_notes_by_diary(id, extended)
    if res is None:
        raise HTTPException(404)
    return res


@router.post("/", status_code=201)
def create_diary(dto: DiaryDto, db: Session = Depends(get_db)):
    check_id_exists_raise(db, Author, dto.author_id)
    service = NoteService(db)
    try:
        return service.create_diary(dto)
    except Exception as e:
        raise HTTPException(400, str(e))


@router.patch("/{id}")
def update_diary(id: int, dto: DiaryDto, db: Session = Depends(get_db)):
    check_id_exists_raise(db, Author, dto.author_id)
    service = NoteService(db)
    res = service.update_diary(id, dto)
    if res is None:
        raise HTTPException(404)
    return res


@router.delete("/{id}", status_code=204)
def delete_diary(id: int, db: Session = Depends(get_db)):
    service = NoteService(db)
    if not service.delete_diary(id):
        raise HTTPException(404)
