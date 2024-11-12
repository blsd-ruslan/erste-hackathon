from sqlalchemy import select

from models.user_model import UserModel
from utils.database import async_session

async def get_user_by_id(user_id: int) -> UserModel:
    async with async_session() as session:
        result = await session.execute(select(UserModel).where(UserModel.id == user_id))
        user = result.scalars().first()  # `scalars()` extracts ORM objects from the result
    return user