from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.notes.dtos import NoteDto, TagDto
from app.notes.service import NoteService

router = APIRouter(prefix="/notes")


@router.get("/filters")
def get_filters(db: Session = Depends(get_db)):
    service = NoteService(db)
    return service.get_filters()


@router.get("/")
def get_all(db: Session = Depends(get_db)):
    service = NoteService(db)
    return service.get_all()


@router.get("/{id}")
def get_one(id: int, extended: bool = True, db: Session = Depends(get_db)):
    service = NoteService(db)
    res = service.get_by_id(id, extended)
    if res is None:
        raise HTTPException(404)
    return res


@router.post("/")
def create(note: NoteDto, db: Session = Depends(get_db)):
    note.validate_ids(db)
    service = NoteService(db)
    try:
        created_note = service.create_note(note)
        return created_note
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/tags")
def create_tag(tag: TagDto, db: Session = Depends(get_db)):
    service = NoteService(db)
    service.create_tag(tag)
