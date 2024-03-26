from sqlalchemy import Column, Integer, String, Float
from app.dependencies.database.database import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    quantity = Column(Integer)
    price = Column(Float)
