import asyncio
import random

from utils.database import async_engine, Base, async_session
from models.user_model import UserModel


def generate_random_user_data():
    # Lists of sample first names and last names
    first_names = ["Alice", "Bob", "Charlie", "Dave", "Eve", "Frank", "Grace", "Heidi", "Ivan", "Judy"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Martinez",
                  "Hernandez"]

    # Generate random username as "FirstLast"
    username = random.choice(first_names) + " " + random.choice(last_names)

    # Other random values
    monthly_spend = random.randint(100, 5000)  # Random spend between $100 and $5000
    year_investments = round(random.uniform(500.0, 20000.0), 2)  # Random investment between $500 and $20000
    month_investments = round(year_investments / 12, 2)  # Roughly split over 12 months

    return {
        "username": username,
        "monthly_spend": monthly_spend,
        "year_investments": year_investments,
        "month_investments": month_investments,
    }


# Async function to insert 40 users
async def insert_random_users():
    async with async_session() as session:
        async with session.begin():  # Start a transaction
            for _ in range(42):
                user_data = generate_random_user_data()
                new_user = UserModel(**user_data)
                session.add(new_user)  # Add to session
        await session.commit()  # Commit all inserts at once

async def init_models():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    await insert_random_users()


if __name__ == "__main__":
    asyncio.run(init_models())