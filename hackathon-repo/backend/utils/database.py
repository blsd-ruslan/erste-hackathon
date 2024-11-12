from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from utils.environment_variables import DATABASE_URL

async_engine = create_async_engine(
    url = DATABASE_URL,
    echo=True,
)

async_session = async_sessionmaker(async_engine)

# async def db_check():
#     async with async_session() as session:
#         result = await session.execute(text("SELECT 1"))
#         print(result.all())
#
# asyncio.run(db_check())

Base = declarative_base()
