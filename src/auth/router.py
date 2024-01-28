from fastapi import APIRouter, Depends

from src.auth.auth_backend import fastapi_users
from src.auth.utils import verifyEmail
from src.database import get_async_session

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@router.get("/confirmation/{token}")
async def confirmation(token: str, db_session=Depends(get_async_session)):
    result = await verifyEmail(token, db_session)
    if result:
        return {"message": "Email is confirmed"}
    return {"message": "Email not confirmed"}