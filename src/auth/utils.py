import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import jwt
from aiosmtplib import SMTP
from sqlalchemy import update

from src.auth.config import secret
from src.auth.models import User


async def send_mail_async(subject, body, to_email, smtp_server, smtp_port, smtp_username, smtp_password, from_email):
    # Создаем MIME-сообщение
    message = MIMEMultipart()
    message['From'] = from_email
    message['To'] = to_email
    message['Subject'] = subject

    message.attach(MIMEText(body, 'plain'))

    async with SMTP(hostname=smtp_server, port=smtp_port, use_tls=True) as smtp:
        await smtp.login(smtp_username, smtp_password)

        await smtp.send_message(message)


async def verifyEmail(token: str, db_session):
    try:
        payload = jwt.decode(token, secret, algorithms="HS256")
        user_email = payload["email"]

        async with db_session as conn:

            await conn.execute(update(User).where(User.email == user_email).values(is_verified=True))
            await conn.commit()

        return True
    except Exception:
        return False