from fastapi import FastAPI, Depends
from typing import Annotated
from sqlalchemy.orm import Session
from .routers import users, problems
from . import security
from .dependencies import get_db
from .crud import create_user

app = FastAPI()

app.include_router(users.router)
app.include_router(problems.router)
app.include_router(security.router)

@app.on_event("startup")
async def startup_event(db: Session = Depends(get_db)):
    create_user(db=db, user={"name": "admin", "password": "123"})


