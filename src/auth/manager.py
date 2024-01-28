from typing import Optional

import jwt
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin

from src.auth.config import secret, smtp_username, smtp_server, smtp_password, smtp_port

from src.auth.models import User

from src.auth.database import get_user_db
from src.auth.utils import send_mail_async

SECRET = secret


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):

        payload = {"email": user.email}

        token = jwt.encode(payload, self.verification_token_secret)

        await send_mail_async(subject="Email confirmation",
                              body=f"http://localhost:9999/auth/confirmation/{token}",
                              to_email=user.email,
                              smtp_server=smtp_server,
                              smtp_port=smtp_port,
                              smtp_username=smtp_username,
                              smtp_password=smtp_password,
                              from_email=smtp_server)

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)