from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import sessionmaker

from app.config import config

DATABASE_URL = str(config.DATABASE_URL)

engine = create_engine(DATABASE_URL)
metadata = MetaData()


engine = create_engine(config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
