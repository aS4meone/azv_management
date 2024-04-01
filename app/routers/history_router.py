import json

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.dependencies.database.database import get_db
from app.dependencies.get_current_user import get_current_user
from app.models.history import History
from app.models.user_model import User
from app.schemas.history_schemas import History as ScHistory

router = APIRouter(tags=['history'])


@router.get("/history/", response_model=List[ScHistory])
async def read_history(
        skip: int = 0, limit: int = 10, history_type: str = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    query = db.query(History).order_by(desc(History.timestamp))

    if history_type:
        query = query.filter(History.history_type == history_type)

    history_entries = query.offset(skip).limit(limit).all()

    corrected_history_entries = []
    for entry in history_entries:
        after_change_json = json.loads(entry.after_change.replace('\\"', ''))

        entry_dict = entry.__dict__
        entry_dict["timestamp"] = entry_dict["timestamp"].isoformat()

        corrected_entry = {
            "username": entry_dict["username"],
            "buyer": entry_dict["buyer"],
            "extra_info": entry_dict["extra_info"],
            "before_change": entry_dict["before_change"],
            "after_change": json.dumps(after_change_json),
            "history_type": entry_dict["history_type"],
            "title": entry_dict["title"],
            "id": entry_dict["id"],
            "timestamp": entry_dict["timestamp"],
            "total_unique_items_count": entry_dict["total_unique_items_count"],  # Добавлено
            "total_items_count": entry_dict["total_items_count"],  # Добавлено
            "total_price": entry_dict["total_price"]  # Добавлено
        }
        corrected_history_entries.append(ScHistory(**corrected_entry))

    return corrected_history_entries

