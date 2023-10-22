from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, AsyncAttrs, async_sessionmaker
from dotenv import dotenv_values
import os


class Base(AsyncAttrs, DeclarativeBase):
    pass


config = {**dotenv_values(".env"), **os.environ}
MYSQL_USER = config["MYSQL_USER"]
MYSQL_PASSWORD = config["MYSQL_PASSWORD"]
MYSQL_HOST = config["MYSQL_HOST"]
MYSQL_PORT = config["MYSQL_PORT"]
MYSQL_DBNAME = config["MYSQL_DBNAME"]

engine = create_async_engine(
    f"mysql+aiomysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DBNAME}"
)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
