from fastapi import FastAPI

from app.authors.controller import router as authors_router
from app.authors.models import init as init_authors
from app.base.models import Base
from app.database import engine
from app.migrations_runner import run_migrations
from app.notes.controller import router as notes_router
from app.notes.diary_controller import router as diaries_router
from app.notes.models import init as init_notes
from app.point.controller import router as points_router
from app.point.models import init as init_point


def init_db():
    # заглушки (чтобы не было ошибок о неиспользуемых импортах)
    # для создания таблиц обязательно импортировать файлы с моделями
    init_authors()
    init_notes()
    init_point()
    Base.metadata.create_all(bind=engine)
    # Накатываем миграции (ALTER/справочники), которые create_all не делает
    # на уже существующих таблицах. Идемпотентны — безопасны при каждом старте.
    run_migrations()
    print("database initialized")


init_db()
app = FastAPI()

app.include_router(authors_router)
app.include_router(notes_router)
app.include_router(points_router)
app.include_router(diaries_router)
