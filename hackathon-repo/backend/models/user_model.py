from sqlalchemy import Column, Integer, String, Float

from utils.database import Base

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    monthly_spend = Column(Integer)
    year_investments = Column(Float)
    month_investments = Column(Float)