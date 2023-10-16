from pydantic import BaseModel

class UserBase(BaseModel):
    name: str
    permission: int

class UserRead(UserBase):
    id: int
    email: str | None = None

    class Config:
        from_attributes: True

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    permission: int | None = None
    password: str | None = None


class ProblemBase(BaseModel):
    name: str
    description: str | None = None
    answer: str
    score_initial: int

class ProblemRead(ProblemBase):
    id: int
    score_now: int

    class Config:
        from_attributes: True

class ProblemCreate(ProblemBase):
    pass

class ProblemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    answer: str | None = None
    score_initial: int | None = None

class Token(BaseModel):
    access_token: str
    token_type: str