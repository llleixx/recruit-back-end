from .database import SessionLocal, engine
from . import models

async def get_db():
    async with SessionLocal() as session:
        yield session