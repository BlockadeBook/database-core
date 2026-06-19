from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.base.query_params import parse_int_csv
from app.base.taxonomy import make_named_taxonomy_router
from app.database import get_db
from app.notes.dtos import NoteDto, NoteFilterParams, TagDto
from app.notes.models import NoteType, Tag, Temporality
from app.notes.service import NoteService

router = APIRouter(prefix="/notes")


@router.get("/filters")
def get_filters(db: Session = Depends(get_db)):
    service = NoteService(db)
    return service.get_filters()


@router.get("/")
def get_all(
    search: Optional[str] = None,
    note_type_ids: Optional[str] = None,
    temporality_ids: Optional[str] = None,
    diary_ids: Optional[str] = None,
    author_ids: Optional[str] = None,
    tag_ids: Optional[str] = None,
    point_ids: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
):
    filters = NoteFilterParams(
        search=search,
        note_type_ids=parse_int_csv(note_type_ids),
        temporality_ids=parse_int_csv(temporality_ids),
        diary_ids=parse_int_csv(diary_ids),
        author_ids=parse_int_csv(author_ids),
        tag_ids=parse_int_csv(tag_ids),
        point_ids=parse_int_csv(point_ids),
        date_from=date_from,
        date_to=date_to,
    )
    service = NoteService(db)
    return service.get_all(filters)


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


@router.patch("/{id}")
def update(id: int, note: NoteDto, db: Session = Depends(get_db)):
    note.validate_ids(db)
    service = NoteService(db)
    try:
        res = service.update_note(id, note)
    except Exception as e:
        raise HTTPException(400, str(e))
    if res is None:
        raise HTTPException(404)
    return res


@router.get("/{id}/edit")
def get_for_edit(id: int, db: Session = Depends(get_db)):
    """Полный состав свидетельства для предзаполнения формы редактирования."""
    service = NoteService(db)
    res = service.get_note_for_edit(id)
    if res is None:
        raise HTTPException(404)
    return res


@router.delete("/{id}", status_code=204)
def delete(id: int, db: Session = Depends(get_db)):
    service = NoteService(db)
    if not service.delete_note(id):
        raise HTTPException(404)


@router.get("/detailed/{id}")
def get_detailed(id: int, db: Session = Depends(get_db)):
    service = NoteService(db)
    res = service.get_detailed_by_id(id)
    if res is None:
        raise HTTPException(404)
    return res


# Legacy POST /notes/tags (no trailing slash) kept for the data loader
@router.post("/tags")
def create_tag(tag: TagDto, db: Session = Depends(get_db)):
    service = NoteService(db)
    return service.create_tag(tag)


# Удаление тега с проверкой использования. Определено ДО подключения generic
# taxonomy-роутера ниже, поэтому перекрывает его DELETE /tags/{id}: тег,
# привязанный к свидетельствам, удалить нельзя (иначе SQLAlchemy молча убрал
# бы связи note_to_tag).
@router.delete("/tags/{id}", status_code=204)
def delete_tag(id: int, db: Session = Depends(get_db)):
    service = NoteService(db)
    try:
        res = service.delete_tag(id)
    except ValueError as e:
        raise HTTPException(409, str(e))
    if res is None:
        raise HTTPException(404)


# Taxonomies — POST /notes/tags/ (trailing slash) plus PATCH/DELETE/list
router.include_router(make_named_taxonomy_router(Tag, "tag_id"), prefix="/tags")
router.include_router(
    make_named_taxonomy_router(NoteType, "note_type_id"), prefix="/note-types"
)
router.include_router(
    make_named_taxonomy_router(Temporality, "temporality_id"),
    prefix="/temporalities",
)
