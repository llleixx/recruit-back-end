from fastapi import Depends, APIRouter, HTTPException, status, Body, Header
from sqlalchemy.orm import Session
from typing import Annotated
from sys import stderr

from ..dependencies import get_db
from .. import crud, schemas, models
from ..security import get_current_user, get_current_user_loose

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

permission_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="You don't have enough permission"
)

email_token_exception = HTTPException(
    status_code=400,
    detail="Wrong email token"
)

@router.get("/rank", response_model=list[schemas.UserRankRead])
async def get_rank(db: Annotated[Session, Depends(get_db)], skip: int = 0, limit: int = 100):
    return await crud.get_rank(db=db, skip=skip, limit=limit)

@router.post("/", response_model=schemas.UserRead)
def create_user(
    *, user: schemas.UserCreate, db: Annotated[Session, Depends(get_db)], current_user: Annotated[models.User | None, Depends(get_current_user_loose)]
):
    if current_user is None:
        if user.permission != 2:
            raise permission_exception
    else:
        if user.permission <= current_user.permission:
            raise permission_exception
    
    db_user = crud.get_user_by_name(db=db, name=user.name)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@router.get("/", response_model=list[schemas.UserRead])
def read_users(*, skip: int = 0, limit: int = 100, db : Annotated[Session, Depends(get_db)]):
    return crud.get_users(db, skip=skip, limit=limit)

@router.get("/{user_id}", response_model=schemas.UserRead)
def read_user(user_id: int, db : Annotated[Session, Depends(get_db)]):
    db_user = crud.get_user(db=db, id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=schemas.UserRead)
def update_user(user_id: int, user: schemas.UserUpdate, db : Annotated[Session, Depends(get_db)], current_user: Annotated[models.User, Depends(get_current_user)], email_token: Annotated[str | None, Header(pattern=r'^\d{6}$', default=None)], email_token1: Annotated[str | None, Header(pattern=r'^\d{6}$', default=None)]):
    db_user = crud.get_user(db=db, id=user_id)
    
    if user_id == current_user.id:
        if user.permission:
            raise permission_exception
    else:
        if (db_user.permission <= current_user.permission) or (user.permission and user.permission <= current_user.permission):
            raise permission_exception
    
    if db_user.email and user.email:
        db_token: models.Confirmation = crud.get_confirmation(db=db, email=db_user.email, option="modify", time_delta=300)
        db_token1: models.Confirmation = crud.get_confirmation(db=db, email=user.email, option="bind", timedelta=300)
        if (db_token and db_token.token == email_token) and (db_token1 and db_token1.token == email_token1):
            pass
        else:
            raise email_token_exception
    
    if db_user.email is None and user.email:
        db_token: models.Confirmation = crud.get_confirmation(db=db, email=db_user.email, option="bind", time_delta=300)
        if db_token.token != email_token:
            raise email_token_exception
    
    if user.password:
        db_token: models.Confirmation = crud.get_confirmation(db=db, email=user.email, option="modify", time_delta=300)
        if db_token.token != email_token:
            raise email_token_exception
    
    if user.name:
        db_user_name: models.User = crud.get_user_by_name(db=db, name=user.name)
        if db_user_name:
            raise HTTPException(
                status_code=400,
                detail="Username already exists"
            )
    
    if user.email:
        db_user_email: models.User = crud.get_user_by_email(db=db, email=user.email)
        if db_user_email:
            raise HTTPException(
                status_code=400,
                detail="User email already exists"
            )

    return crud.update_user(db=db, user_id=user_id, user=user)

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)], current_user: Annotated[models.User, Depends(get_current_user)]):
    db_user = crud.get_user(db=db, id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    if db_user.permission <= current_user.permission:
        raise permission_exception
    
    crud.delete_user(db, user_id)

@router.post("/{user_id}/problems/{problem_id}")
def answer_problem(user_id: int, problem_id: int, db: Annotated[Session, Depends(get_db)], current_user: Annotated[models.User, Depends(get_current_user)], answer: Annotated[str, Body(embed=True)]):
    if current_user.id != user_id:
        raise permission_exception
    
    db_user: models.User = crud.get_user(db=db, id=user_id)
    db_problem: models.Problem = crud.get_problem(db=db, id=problem_id)

    response = {"status": ""}
    
    if db_problem.answer == answer:
        response["status"] = "Accepted"
        crud.answer(user=db_user, problem=db_problem, db=db)
    else:
        response["status"] = "Wrong"
    
    return response