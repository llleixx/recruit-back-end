from fastapi import Depends, APIRouter, HTTPException, status, Body, Header
from sqlalchemy.orm import Session
from typing import Annotated
from sys import stderr
from datetime import timedelta
from enum import Enum
import random, string

from ..security import get_current_user
from ..dependencies import get_db
from .. import crud, schemas, models
from .. import security
from ..email import send_email_base


router = APIRouter(
    tags=["others"],
)

MESSAGE = {
    "LOGIN": {
        "subject": "xx - New Login",
        "content":
        """
<html>
<body>
<b style="font-size: 24px;">Enter the vertification code to login in:</b>
<div style="text-align: center">
    <span style="vertical-align: center; font-size: 24px">{}</span>
</div>
</body>
</html>
"""
    },
    "BIND": {
        "subject": "xx - New Bind",
        "content":
        """
<html>
<body>
<b style="font-size: 24px;">Enter the vertification code to bind your email:</b>
<div style="text-align: center">
    <span style="vertical-align: center; font-size: 24px;">{}</span>
</div>
</body>
</html>
"""
    },
    "MODIFY": {
        "subject": "xx - Modify",
        "content":
        """
<html>
<body>
<b style="font-size: 24px;">Enter the vertification code to bind your email:</b>
<div style="text-align: center">
    <span style="vertical-align: center; font-size: 24px;">{}</span>
</div>
</body>
</html>
"""
    }
}

@router.post("/token", response_model=security.Token)
def login_for_access_token(
    form_data: Annotated[security.OAuth2PasswordRequestForm, Depends()],
):
    user = security.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/sendEmail")
async def send_email(*, sendEmailRequest: schemas.SendEMailRequest, db: Annotated[Session, Depends(get_db)]):
    if sendEmailRequest.option not in MESSAGE.keys():
        raise HTTPException(
            status_code=404,
            detail="sendEmail don't have such operation"
        )
    
    if crud.get_confirmation(db=db, **sendEmailRequest.model_dump(), time_delta=60):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have snet such email, please wait."
        )

    token: str = ''.join(random.choices(string.digits, k=6))
    crud.create_confirmation(db=db, **sendEmailRequest.model_dump(), token=token)

    try:
        await send_email_base(to_users=sendEmailRequest.email, subject=MESSAGE[sendEmailRequest.option]["subject"], content=MESSAGE[sendEmailRequest.option]["content"].format(token))
    except Exception as e:
        print(e, file=stderr)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Can't send email"
        )

    return {"detail": "Success"}

@router.get("/me", response_model=schemas.UserRead)
def get_me(current_user: Annotated[models.User, Depends(get_current_user)]):
    return current_user