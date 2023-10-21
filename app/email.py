import aiosmtplib, ssl
from email.message import EmailMessage
from dotenv import dotenv_values
from sys import stderr
from typing import Annotated
from fastapi import Header, Depends
from sqlalchemy.orm import Session
from .dependencies import get_db
import os

config = {
    **dotenv_values(".env"),
    **os.environ
}

EMAIL_HOST = config["EMAIL_HOST"]
EMAIL_PORT = int(config["EMAIL_PORT"])
EMAIL_USER = config["EMAIL_USER"]
EMAIL_AUTH = config["EMAIL_AUTH"]

async def send_email_base(to_users, subject='', content=''):
    message = EmailMessage()
    message['From'] = EMAIL_USER
    message['To'] = to_users
    message['Subject'] = subject

    message.set_content(content, 'html')

    async with aiosmtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        await server.login(EMAIL_USER, EMAIL_AUTH)
        await server.send_message(message)