from fastapi import FastAPI, Depends
from typing import Annotated
from sqlalchemy.orm import Session
from .routers import users, problems, others
from . import security
from .dependencies import SessionLocal, engine
from .models import Base
from . import crud
from .schemas import UserCreate

app = FastAPI()

app.include_router(users.router)
app.include_router(problems.router)
app.include_router(security.router)
app.include_router(others.router)

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with SessionLocal() as db:
        user = await crud.get_user(db, 1)
        if user is None:
            await crud.create_user(db=db, user=UserCreate(name="admin", permission=0, password="123"))

