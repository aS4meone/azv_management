from pytz import timezone, utc
from sqlalchemy import Column, Integer, String, Text, DateTime, text
from sqlalchemy.sql import func
from app.dependencies.database.database import Base


class History(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    username = Column(String)
    buyer = Column(String, nullable=True)
    extra_info = Column(Text, nullable=True)
    before_change = Column(Text, nullable=True)
    after_change = Column(Text)
    history_type = Column(String)
    title = Column(String)