from pydantic import BaseModel, Field
from typing import Annotated

class UserBase(BaseModel):
    name: Annotated[str, Field(pattern=r'^\w{2, 8}$')]
    permission: Annotated[int, Field(ge=0, le=2)]

class UserRead(UserBase):
    id: int
    email: str | None

    class Config:
        from_attributes: True

class UserRankRead(BaseModel):
    id: int
    name: str
    total_score: int

    class Config:
        from_attributes: True

class UserCreate(UserBase):
    password: Annotated[str, Field(pattern=r'^\w{2, 16}$')]

class UserUpdate(BaseModel):
    name: str | None = Field(pattern=r'^\w{2, 16}$', default=None)
    email: str | None = Field(pattern=r'^([a-z0-9_\.-]+)@([\da-z\.-]+)\.([a-z\.]{2,6})$', default=None)
    permission: int | None = Field(ge=0, le=2, default=None)
    password: str | None = Field(pattern=r'^\w{2, 16}$', default=None)


class ProblemBase(BaseModel):
    name: str
    description: str | None = None
    answer: str | None
    score_initial: Annotated[int, Field(default=None, multiple_of=10, ge=10, le=10000)]

class ProblemRead(ProblemBase):
    id: int
    owner_id: int
    score_now: int

    class Config:
        from_attributes: True

class ProblemCreate(ProblemBase):
    owner_id: int | None = Field(
        description="It's based on your logined account. It's no need to pass this field.",
        default= None
    )
    pass

class ProblemUpdate(BaseModel):
    name: str | None = Field(max_length=64, default=None)
    owner_id: int | None = Field(default=None)
    description: str | None = Field(default=None)
    answer: str | None = Field(default=None)
    score_initial: int | None = Field(default=None, multiple_of=10, ge=10)

class Token(BaseModel):
    access_token: str
    token_type: str

class SendEMailRequest(BaseModel):
    option: str
    email: str