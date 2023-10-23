from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exc
from sqlalchemy.sql import func, desc
from datetime import datetime, timedelta
from fastapi import HTTPException
from . import models, schemas
from .security import pwd_context


async def get_user(db: AsyncSession, id: int):
    return await db.get(models.User, id)


async def get_user_by_email(db: AsyncSession, email: str):
    return (
        await db.scalars(select(models.User).where(models.User.email == email))
    ).first()


async def get_user_by_name(db: AsyncSession, name: str):
    return (
        await db.scalars(select(models.User).where(models.User.name == name))
    ).first()


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    return (await db.scalars(select(models.User).offset(skip).limit(limit))).all()


async def update_user(db: AsyncSession, user_id: int, user: schemas.UserUpdate):
    db_user = await get_user(db=db, id=user_id)
    update_user = user.model_dump(exclude_unset=True)
    for key, val in update_user.items():
        setattr(db_user, key, val)
    await db.commit()
    return db_user


async def create_user(db: AsyncSession, user: schemas.UserCreate):
    db_user = models.User(**user.model_dump())
    db_user.password = pwd_context.hash(db_user.password)
    try:
        db.add(db_user)
        await db.commit()
    except exc.IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="name or email already exists"
        )
    return db_user


async def delete_user(db: AsyncSession, id: int):
    await db.delete(await db.get(models.User, id))
    await db.commit()


async def get_problem(db: AsyncSession, id: int):
    return await db.get(models.Problem, id)


async def get_problem_by_name(db: AsyncSession, name: str):
    return (
        await db.scalars(select(models.Problem).where(models.Problem.name == name))
    ).first()


async def get_problems(db: AsyncSession, skip: int = 0, limit: int = 100):
    return (await db.scalars(select(models.Problem).offset(skip).limit(limit))).all()


async def create_problem(db: AsyncSession, problem: schemas.ProblemCreate):
    db_problem = models.Problem(**problem.model_dump(), score_now=problem.score_initial)
    db.add(db_problem)
    await db.commit()
    return db_problem


async def update_problem(
    db: AsyncSession, problem_id: int, problem: schemas.ProblemUpdate
):
    db_problem: models.Problem = await get_problem(db=db, id=problem_id)
    update_problem = problem.model_dump(exclude_unset=True)
    if problem.score_initial:
        db_problem.score_now = (
            problem.score_initial * db_problem.score_now / db_problem.score_initial
        )
    for key, val in update_problem.items():
        setattr(db_problem, key, val)
    try:
        await db.commit()
    except exc.IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="name or email already exists"
        )
    return db_problem


async def delete_problem(db: AsyncSession, id: int):
    await db.delete(await db.get(models.Problem, id))
    await db.commit()


async def answer(db: AsyncSession, user: models.User, problem: models.Problem):
    if problem not in await user.awaitable_attrs.problems:
        if problem.score_now != problem.score_initial / 10:
            problem.score_now -= problem.score_initial / 10

        user.problems.append(problem)
        await db.commit()


async def get_rank(db: AsyncSession, skip: int = 0, limit=50):
    return (
        await db.execute(
            select(
                models.User.id,
                models.User.name,
                func.sum(models.Problem.score_now).label("total_score"),
            )
            .select_from(models.UserProblemLink)
            .join(models.Problem)
            .join(models.User)
            .group_by(models.UserProblemLink.c.user_id)
            .offset(skip)
            .limit(limit)
            .order_by(desc("total_score"))
        )
    ).all()


async def get_confirmation(db: AsyncSession, email: str, option: str, time_delta: int):
    last_time = datetime.utcnow() - timedelta(seconds=time_delta)
    return (
        await db.scalars(
            select(models.Confirmation)
            .where(
                models.Confirmation.create_time > last_time,
                models.Confirmation.email == email,
                models.Confirmation.option == option,
            )
            .order_by(models.Confirmation.create_time)
        )
    ).first()


async def create_confirmation(db: AsyncSession, email: str, option: str, token: str):
    db_confirmation = models.Confirmation(email=email, option=option, token=token)
    await db.merge(db_confirmation)
    await db.commit()
