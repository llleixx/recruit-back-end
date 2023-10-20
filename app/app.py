from fastapi import FastAPI, Depends
from .routers import users, problems, others
from . import security
from .dependencies import SessionLocal
from .database import engine
from .models import Base
from . import crud
from .schemas import UserCreate
from dotenv import dotenv_values
import re
from sys import stderr
from contextlib import asynccontextmanager

class WrongConfigEnv(Exception):
    def __init__(self, config_key: str):
        self.config_key = config_key

    
    def __str__(self):
        return f"Wrong config: {self.config_key}"

config = dotenv_values(".env")


USER_NAME_REGEX = re.compile(r'^\w{2,16}$')
USER_PASSWORD_REGEX = re.compile(r'^\w{2,16}$')

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with SessionLocal() as db:
        user = await crud.get_user(db, 1)
        if user is None:
            INITIAL_USER_NAME = config["INITIAL_USER_NAME"]
            INITIAL_USER_PASSWORD = config["INITIAL_USER_PASSWORD"]

            if USER_NAME_REGEX.match(INITIAL_USER_NAME) is None:
                raise WrongConfigEnv("INITIAL_USER_NAME")
            
            if USER_PASSWORD_REGEX.match(INITIAL_USER_PASSWORD) is None:
                raise WrongConfigEnv("INITIAL_USER_PASSWORD")

            await crud.create_user(db=db, user=UserCreate(name=INITIAL_USER_NAME, permission=0, password=INITIAL_USER_PASSWORD))

    yield

app = FastAPI(lifespan=lifespan)

app.include_router(users.router)
app.include_router(problems.router)
app.include_router(security.router)
app.include_router(others.router)