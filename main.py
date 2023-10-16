from fastapi import FastAPI
from .routers import users, problems

app = FastAPI()

app.include_router(users.router)
app.include_router(problems.router)
