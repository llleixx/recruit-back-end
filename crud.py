from sqlalchemy.orm import Session
from sqlalchemy import select
from . import models, schemas

def get_user(db: Session, id: int):
    return db.get(models.User, id)

def get_user_by_email(db: Session, email: str):
    return db.scalars(
        select(models.User).where(models.User.email == email)
    ).first()

def get_user_by_name(db: Session, name: str):
    return db.scalars(
        select(models.User).where(models.User.name == name)
    ).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.scalars(
        select(models.User).offset(skip).limit(limit)
    ).all()

def update_user(db: Session, user_id: int, user: schemas.UserUpdate):
    db_user = get_user(db=db, id=user_id)
    update_user = user.model_dump(exclude_unset=True)
    for key, val in update_user.items():
        setattr(db_user, key, val)
    db.add(db_user) # no need ?
    db.commit()
    db.refresh(db_user)
    return db_user

def create_user(db: Session, user: schemas.UserCreate):
    user.passwd = user.passwd
    db_user = models.User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, id: int):
    db.delete(db.get(models.User, id))
    db.commit()

def get_problem(db: Session, id: int):
    return db.get(models.Problem, id)

def get_problem_by_name(db: Session, name: str):
    return db.scalars(
        select(models.Problem).where(models.Problem.name == name)
    ).first()

def get_problems(db: Session, skip: int = 0, limit: int = 100):
    return db.scalars(
        select(models.Problem).offset(skip).limit(limit)
    ).all()

def create_problem(db: Session, problem: schemas.ProblemCreate):
    db_problem = models.Problem(**problem.model_dump(), score_now=problem.score_initial)
    db.add(db_problem)
    db.commit()
    db.refresh(db_problem)
    return db_problem

def update_problem(db: Session, problem_id: int,  problem: schemas.ProblemUpdate):
    db_problem = get_problem(db=db, id=problem_id)
    update_problem = problem.model_dump(exclude_unset=True)
    for key, val in update_problem.items():
        setattr(db_problem, key, val)
    db.add(db_problem)
    db.commit()
    db.refresh(db_problem)
    return db_problem

def delete_problem(db: Session, id: int):
    db.delete(db.get(models.Problem, id))
    db.commit()