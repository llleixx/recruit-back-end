from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from sqlalchemy import create_engine

class Base(DeclarativeBase):
    pass

engine = create_engine(
    "sqlite:///./sql_app.db", connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(engine)