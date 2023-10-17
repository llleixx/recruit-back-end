from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated
from sys import stderr

from ..dependencies import get_db
from .. import crud, schemas, models
from ..security import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

permission_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="You don't have enough permission"
)

login_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="You must login to finish this operation"
)

@router.post("/", response_model=schemas.UserRead)
def create_user(
    *, user: schemas.UserCreate, db: Annotated[Session, Depends(get_db)], current_user: Annotated[models.User | None, Depends(get_current_user)]
):
    if current_user is None:
        if user.permission != 2:
            raise login_exception
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
def update_user(user_id: int, user: schemas.UserUpdate, db : Annotated[Session, Depends(get_db)], current_user: Annotated[models.User, Depends(get_current_user)]):
    if current_user is None:
        raise login_exception

    db_user = crud.get_user(db=db, id=user_id)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    if user_id == current_user.id:
        if user.permission:
            raise permission_exception
    else:
        if (db_user.permission <= current_user.permission) or (user.permission and user.permission <= current_user.permission):
            raise permission_exception

    return crud.update_user(db=db, user_id=user_id, user=user)

@router.delete("/{user_id}")
def delete_user(user_id: int, db : Annotated[Session, Depends(get_db)], current_user: Annotated[models.User, Depends(get_current_user)]):
    if current_user is None:
        raise permission_exception

    db_user = crud.get_user(db=db, id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    if db_user.permission <= current_user.permission:
        raise permission_exception
    
    crud.delete_user(db, user_id)