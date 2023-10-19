from __future__ import annotations

from sqlalchemy import Column, Table, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

UserProblemLink = Table(
    "userproblemlink",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("problem_id", ForeignKey("problems.id"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str | None] = None
    password: Mapped[str]
    permission: Mapped[int]

    problems: Mapped[list[Problem]] = relationship(
        secondary=UserProblemLink, back_populates="users"
    )

class Problem(Base):
    __tablename__ = "problems"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int]
    name: Mapped[str]
    description: Mapped[str | None] = None
    answer: Mapped[str]
    score_initial: Mapped[int]
    score_now: Mapped[int]

    users: Mapped[list[User]] = relationship(
        secondary=UserProblemLink, back_populates="problems"
    )

class Confirmation(Base):
    __tablename__ = "confirmations"

    email: Mapped[str] = mapped_column(primary_key=True)
    option: Mapped[str] = mapped_column(primary_key=True)
    token: Mapped[str]
    create_time: Mapped[datetime] = mapped_column(DateTime(), server_default=func.now(), default=func.now(), onupdate=func.now())
    