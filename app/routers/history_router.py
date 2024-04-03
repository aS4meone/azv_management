import json

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, or_
from sqlalchemy.orm import Session

from app.dependencies.database.database import get_db
from app.dependencies.get_current_user import get_current_user
from app.models.history import History
from app.models.user_model import User
from app.schemas.history_schemas import History as ScHistory

router = APIRouter(tags=['history'])


@router.get("/history/", response_model=List[ScHistory])
async def read_history(
        skip: int = 0, limit: int = 10, history_type: str = None, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
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
            "total_unique_items_count": entry_dict["total_unique_items_count"],
            "total_items_count": entry_dict["total_items_count"],
            "total_price": entry_dict["total_price"]
        }
        corrected_history_entries.append(ScHistory(**corrected_entry))

    return corrected_history_entries


@router.get("/history/search/", response_model=List[ScHistory])
async def search_history(
        query_string: str, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    # Разбиваем строку запроса на отдельные слова
    search_terms = query_string.split()

    # Формируем условие для поиска по текстовым колонкам
    search_filter = or_(
        *[getattr(History, column_name).ilike(f'%{term}%') for term in search_terms
          for column_name in ['username', 'buyer', 'extra_info', 'before_change',
                              'after_change', 'history_type', 'title']]
    )

    # Выполняем запрос с учетом фильтрации
    history_entries = (
        db.query(History)
        .filter(search_filter)
        .order_by(desc(History.timestamp))
        .all()
    )

    # Преобразуем результаты запроса в соответствующий формат
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
            "total_unique_items_count": entry_dict["total_unique_items_count"],
            "total_items_count": entry_dict["total_items_count"],
            "total_price": entry_dict["total_price"]
        }
        corrected_history_entries.append(ScHistory(**corrected_entry))

    return corrected_history_entries


@router.delete("/history/{history_id}/")
async def delete_history_entry(history_id: int, db: Session = Depends(get_db)):
    history_entry = db.query(History).filter(History.id == history_id).first()

    if not history_entry:
        raise HTTPException(status_code=404, detail="History date not found")

    db.delete(history_entry)
    db.commit()

    return {"message": "Success"}
