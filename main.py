from fastapi import FastAPI, Depends
from typing import Annotated
from sqlalchemy.orm import Session
from .routers import users, problems
from . import security
from .dependencies import SessionLocal
from . import crud
from .schemas import UserCreate
from os import path

app = FastAPI()

app.include_router(users.router)
app.include_router(problems.router)
app.include_router(security.router)

@app.on_event("startup")
async def startup_event():
    with SessionLocal() as db:
        user = crud.get_user(db, 1)
        if user is None:
            crud.create_user(db=db, user=UserCreate(name="admin", permission=0, password="123"))

