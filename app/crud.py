from sqlalchemy.orm import Session, aliased
from sqlalchemy import select
from sqlalchemy.sql import func, desc
from datetime import datetime, timedelta
from . import models, schemas
from .security import pwd_context
from sys import stderr

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
    db_user = models.User(**user.model_dump())
    db_user.password = pwd_context.hash(db_user.password)
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
    if problem.score_initial:
        db_problem.score_now = problem.score_initial * db_problem.score_now / db_problem.score_initial
    for key, val in update_problem.items():
        setattr(db_problem, key, val)
    db.add(db_problem)
    db.commit()
    db.refresh(db_problem)
    return db_problem

def delete_problem(db: Session, id: int):
    db.delete(db.get(models.Problem, id))
    db.commit()

def answer(db: Session, user: models.User, problem: models.Problem):
    if problem not in user.problems:
        if problem.score_now != problem.score_initial / 10:
            problem.score_now -= problem.score_initial / 10
        
        user.problems.append(problem)
        db.commit()
    
async def get_rank(db: Session, skip: int = 0, limit=50):
    res = db.execute(
        select(models.User.id, models.User.name, func.sum(models.Problem.score_now).label("total_score")).select_from(models.UserProblemLink).join(models.Problem).join(models.User).group_by(models.UserProblemLink.c.user_id).offset(skip).limit(limit).order_by(desc("total_score"))
    ).all()

    return res

def get_confirmation(db: Session, email: str, option: str, time_delta: int):
    last_time = datetime.utcnow() - timedelta(seconds=time_delta)
    res = db.scalars(
        select(models.Confirmation).where(
            models.Confirmation.create_time > last_time, models.Confirmation.email == email, models.Confirmation.option == option
        ).order_by(models.Confirmation.create_time)
    ).first()
    return res

def create_confirmation(db: Session, email: str, option: str, token: str):
    db_confirmation = models.Confirmation(email=email, option=option, token=token)
    db.merge(db_confirmation)
    db.commit()