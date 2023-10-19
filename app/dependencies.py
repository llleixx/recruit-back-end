from .database import SessionLocal, engine
from . import models

models.Base.metadata.create_all(engine)

def get_db():
    with SessionLocal() as db:
        yield db