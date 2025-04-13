from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.authors.dtos import AuthorDto
from app.authors.service import AuthorService
from app.database import get_db

router = APIRouter(prefix="/authors")


@router.get("/filters")
def get_filters(db: Session = Depends(get_db)):
    author_service = AuthorService(db)
    return author_service.get_filters()


@router.get("/")
def get_all(db: Session = Depends(get_db)):
    author_service = AuthorService(db)
    return author_service.get_all()


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
