from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.notes.service import NoteService

router = APIRouter(prefix="/diaries")


@router.get("/")
def get_all(db: Session = Depends(get_db)):
    service = NoteService(db)
    return service.get_all_diaries()


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
