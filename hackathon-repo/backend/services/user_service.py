from repositories import user_repository

async def get_user(user_id: int):
    user = await user_repository.get_user_by_id(user_id)
    return user