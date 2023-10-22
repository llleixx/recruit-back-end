from fastapi import Depends, APIRouter, HTTPException, status, Body, Header, Query, Path
from sqlalchemy.orm import Session
from typing import Annotated

from ..dependencies import get_db
from .. import crud, schemas, models
from ..security import get_current_user, get_current_user_loose, get_current_user_strict

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

permission_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN, detail="You don't have enough permission"
)

email_token_exception = HTTPException(status_code=400, detail="Wrong email token")


@router.get("/rank", response_model=list[schemas.UserRankRead])
async def get_rank(
    db: Annotated[Session, Depends(get_db)],
    skip: Annotated[int, Query(description="the offset")] = 0,
    limit: Annotated[int, Query(description="the max number display")] = 100,
):
    """
    Get the rank list of users with id, name and total_score.
    """
    return await crud.get_rank(db=db, skip=skip, limit=limit)


@router.post("/", response_model=schemas.UserRead)
async def create_user(
    *,
    user: schemas.UserCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User | None, Depends(get_current_user_strict)]
):
    """
    Create an user.

    If your are loggined and your permission equal to or less than 1, then you have the permission to create a user wiht permission greater than yours.

    Or you can just register a user with permission which equals to 1.

    - **name**: the user's name, you can login with this
    - **permission**: 0, 1, 2. The less it is, your permission is greater
    - **password**: the user's password
    """
    if current_user is None:
        if user.permission != 2:
            raise permission_exception
    else:
        if user.permission <= current_user.permission:
            raise permission_exception

    db_user = await crud.get_user_by_name(db=db, name=user.name)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return await crud.create_user(db=db, user=user)


@router.get("/", response_model=list[schemas.UserRead])
async def read_users(
    *,
    skip: Annotated[int, Query(description="the offset")] = 0,
    limit: Annotated[int, Query(description="the max number display")] = 100,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Read users' information.
    """
    return await crud.get_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=schemas.UserRead)
async def read_user(
    user_id: Annotated[int, Path(description="the user's id you want to read")],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Read a user with user's id.
    """
    db_user = await crud.get_user(db=db, id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.put("/{user_id}", response_model=schemas.UserRead)
async def update_user(
    user_id: int,
    user: schemas.UserUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(get_current_user)],
    email_token: Annotated[
        str | None,
        Header(
            pattern=r"^\d{6}$",
            description="use the token to modify your password or email",
        ),
    ] = None,
    email_token1: Annotated[
        str | None,
        Header(
            pattern=r"^\d{6}$",
            description="it is needed when you want to alter your email",
        ),
    ] = None,
):
    """
    Update a user's information.

    You need email token as header to modify your sensitive infomation.
    """
    db_user: models.User = await crud.get_user(db=db, id=user_id)

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # 重复检测
    if user.name:
        db_user_name: models.User = await crud.get_user_by_name(db=db, name=user.name)
        if db_user_name:
            raise HTTPException(status_code=400, detail="Username already exists")

    if user.email:
        db_user_email: models.User = await crud.get_user_by_email(
            db=db, email=user.email
        )
        if db_user_email:
            raise HTTPException(status_code=400, detail="User email already exists")

    # 当前用户权限更大
    if db_user.permission > current_user.permission:
        return await crud.update_user(db=db, user_id=user_id, user=user)

    # 权限不更大且不是自己则非法
    if db_user.id != current_user.id:
        raise permission_exception

    # 是自己
    if db_user.email and user.email:
        db_token: models.Confirmation = await crud.get_confirmation(
            db=db, email=db_user.email, option="MODIFY", time_delta=300
        )
        db_token1: models.Confirmation = await crud.get_confirmation(
            db=db, email=user.email, option="BIND", time_delta=300
        )
        if (db_token and db_token.token == email_token) and (
            db_token1 and db_token1.token == email_token1
        ):
            pass
        else:
            raise email_token_exception

    if db_user.email is None and user.email:
        db_token: models.Confirmation = await crud.get_confirmation(
            db=db, email=user.email, option="BIND", time_delta=300
        )
        if db_token is None or db_token.token != email_token:
            raise email_token_exception

    if user.password:
        db_token: models.Confirmation = await crud.get_confirmation(
            db=db, email=user.email, option="MODIFY", time_delta=300
        )
        if db_token is None or db_token.token != email_token:
            raise email_token_exception

    return await crud.update_user(db=db, user_id=user_id, user=user)


@router.delete(
    "/{user_id}",
    responses={
        "200": {"content": {"application/json": {"example": {"detail": "SUCCESS"}}}}
    },
)
async def delete_user(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(get_current_user)],
):
    """
    Delete a user.

    Current user's permission should less than the user_id's permission.
    """
    db_user: models.User = await crud.get_user(db=db, id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if db_user.permission <= current_user.permission:
        raise permission_exception

    await crud.delete_user(db, user_id)

    return {"detail": "SUCCESS"}


@router.post(
    "/{user_id}/problems/{problem_id}", response_model=schemas.AnswerProblemResponse
)
async def answer_problem(
    user_id: int,
    problem_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(get_current_user_strict)],
    answer: Annotated[str, Body(embed=True)],
):
    """
    Answer a problem.

    The user_id must be your current user's id.
    """
    if current_user.id != user_id:
        raise permission_exception

    db_user: models.User = await crud.get_user(db=db, id=user_id)
    db_problem: models.Problem = await crud.get_problem(db=db, id=problem_id)

    if db_problem is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Such problem don't exist"
        )

    response_message: str

    if db_problem.answer == answer:
        response_message = "ACCEPTED"
        await crud.answer(user=db_user, problem=db_problem, db=db)
    else:
        response_message = "WRONG"

    return {"detail": response_message}
