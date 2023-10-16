from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from . import crud, models, schemas

models.Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    with SessionLocal() as db:
        yield db