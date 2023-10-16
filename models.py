from __future__ import annotations

from sqlalchemy import Column
from sqlalchemy import Table
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from .database import Base

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
    name: Mapped[str]
    description: Mapped[str | None] = None
    answer: Mapped[str]
    score_initial: Mapped[int]
    score_now: Mapped[int]

    users: Mapped[list[User]] = relationship(
        secondary=UserProblemLink, back_populates="problems"
    )

    



