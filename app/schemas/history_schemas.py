from pydantic import BaseModel, Field, Json
from typing import Optional, Any, Union
from datetime import datetime


class HistoryBase(BaseModel):
    username: str
    buyer: Optional[str] = None
    extra_info: Optional[str] = None
    before_change: Optional[Json[Any]] = None
    after_change: Json[Any]
    history_type: str
    title: Optional[str] = None
    total_unique_items_count: Optional[int] = None
    total_items_count: Optional[int] = None
    total_price: Optional[float] = None


class HistoryCreate(HistoryBase):
    pass


class History(HistoryBase):
    id: int
    timestamp: datetime = Field(..., description="Timestamp of the history entry")

    class Config:
        orm_mode = True
