import uvicorn as uvicorn
from fastapi import FastAPI
from src.auth.auth_backend import auth_backend, fastapi_users

from src.api.map.router import router as city_router
from src.api.shop.router import router as shop_router
from src.api.admin.router import router as admin_router
from src.auth.schemas import UserRead, UserCreate


app = FastAPI()

app.include_router(
    city_router
)

app.include_router(
    shop_router
)

app.include_router(
    admin_router
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)


app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)


app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)


if __name__ == "__main__":
    uvicorn.run(app=app, port=9999, host="0.0.0.0")