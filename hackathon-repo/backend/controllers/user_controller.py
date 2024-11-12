from fastapi import APIRouter
from services import user_service

user_router = APIRouter()

@user_router.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await user_service.get_user(user_id)

    return user
