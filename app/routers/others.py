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

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: Annotated[security.OAuth2PasswordRequestForm, Depends()],
):
    """
    Get token to login.

    Notice that you should send username and password with multipart/form-data.

    - **username**: Your account, email or name
    - **password**: Your password. If you login with email, it can be the email token
    """
    user = await security.authenticate_user(form_data.username, form_data.password)
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

@router.post("/sendEmail", responses={
    "200": {
        "content": {
            "application/json": {
                "example": {"detail": "SUCCESS"}
            }
        }}
})
async def send_email(sendEmailRequest: schemas.SendEMailRequest, db: Annotated[Session, Depends(get_db)]):
    """
    Send email to help you authenticate to finish some dangerous behaviors.

    - **option**: The value should be mong "BIND" "LOGIN" "MODIFY"
    - **email**: The email you want to operate with
    """
    if await crud.get_confirmation(db=db, email=sendEmailRequest.email, option=sendEmailRequest.option.value, time_delta=300):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have snet such email, please wait."
        )

    try:
        await send_email_base(to_users=sendEmailRequest.email, subject=MESSAGE[sendEmailRequest.option.value]["subject"], content=MESSAGE[sendEmailRequest.option.value]["content"].format(token))
    except Exception as e:
        print(e, file=stderr)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Can't send email because: {e}"
        )

    token: str = ''.join(random.choices(string.digits, k=6))
    await crud.create_confirmation(db=db, email=sendEmailRequest.email, option=sendEmailRequest.option.value, token=token)


    return {"detail": "Success"}

@router.get("/me", response_model=schemas.UserRead)
async def get_me(current_user: Annotated[models.User, Depends(get_current_user)]):
    """
    Get the current user's information.
    """
    return current_user