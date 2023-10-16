from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated

from ..dependencies import get_db
from ..security import get_current_user
from .. import crud, schemas, models

router = APIRouter(
    prefix="/problems",
    tags=["problems"]
)

@router.post("/", response_model=schemas.ProblemRead)
def create_problem(problem: schemas.ProblemCreate, db : Annotated[Session, Depends(get_db)], current_user: Annotated[models.User, Depends(get_current_user)]):
    db_problem = crud.get_problem_by_name(db=db, name=problem.name)
    if db_problem:
        raise HTTPException(status_code=400, detail="Problem name already registered")
    return crud.create_problem(db=db, problem=problem)

@router.get("/", response_model=list[schemas.ProblemRead])
def read_problems(*, skip: int = 0, limit: int = 100, db : Annotated[Session, Depends(get_db)]):
    return crud.get_problems(skip=skip, limit=limit, db=db)

@router.get("/{problem_id}", response_model=schemas.ProblemRead)
def read_problem(problem_id: int, db : Annotated[Session, Depends(get_db)]):
    db_problem = crud.get_problem(db=db, id=problem_id)
    if db_problem is None:
        raise HTTPException(status_code=404, detail="Problem not found")
    return db_problem

@router.put("/{problem_id}", response_model=schemas.ProblemRead)
def update_problem(problem_id: int, problem: schemas.ProblemUpdate, db : Annotated[Session, Depends(get_db)], current_user: Annotated[models.User, Depends(get_current_user)]):
    db_problem = crud.get_problem(db=db, id=problem_id)
    if db_problem is None:
        raise HTTPException(status_code=404, detail="Problem not found")
    return crud.update_problem(db=db, problem_id=problem_id, problem=problem)

@router.delete("/{problem_id}")
def delete_problem(problem_id: int, db : Annotated[Session, Depends(get_db)], current_user: Annotated[models.User, Depends(get_current_user)]):
    db_problem = crud.get_problem(db=db, id=problem_id)
    if db_problem is None:
        raise HTTPException(status_code=404, detail="Problem not found")
    crud.delete_problem(db, problem_id)