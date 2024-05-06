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
        if entry.before_change:
            before_change_json = json.loads(entry.before_change.replace('\\"', ''))
        else:
            before_change_json = None
        entry_dict = entry.__dict__
        entry_dict["timestamp"] = entry_dict["timestamp"].isoformat()

        corrected_entry = {
            "username": entry_dict["username"],
            "buyer": entry_dict["buyer"],
            "extra_info": entry_dict["extra_info"],
            "before_change": json.dumps(before_change_json, ensure_ascii=False),
            "after_change": json.dumps(after_change_json, ensure_ascii=False),
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
        query_string: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    query = db.query(History)

    for entry in query:
        if entry.before_change:
            entry.before_change = json.loads(entry.before_change.replace('\\"', ''))
        if entry.after_change:
            entry.after_change = json.loads(entry.after_change.replace('\\"', ''))


    column_filters = [
        History.username.ilike(f"%{query_string}%"),
        History.buyer.ilike(f"%{query_string}%"),
        History.extra_info.ilike(f"%{query_string}%"),
        History.before_change.ilike(f"%{query_string}%"),
        History.after_change.ilike(f"%{query_string}%"),
        History.history_type.ilike(f"%{query_string}%"),
        History.title.ilike(f"%{query_string}%"),
    ]

    query = query.filter(or_(*column_filters)).order_by(desc(History.timestamp))
    history_entries = query.all()

    corrected_history_entries = []
    for entry in history_entries:
        entry_dict = entry.__dict__
        entry_dict["timestamp"] = entry_dict["timestamp"].isoformat()

        corrected_entry = {
            "username": entry_dict["username"],
            "buyer": entry_dict["buyer"],
            "extra_info": entry_dict["extra_info"],
            "before_change": json.dumps(entry.before_change, ensure_ascii=False) if entry.before_change else None,
            "after_change": json.dumps(entry.after_change, ensure_ascii=False) if entry.after_change else None,
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


def fix_unicode_in_database(db: Session, json_data):
    # Парсим JSON данные
    try:
        data = json.loads(json_data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Невозможно разобрать строку JSON")

    # Исправляем Unicode-последовательности в поле 'name' внутри JSON в полях 'before_change' и 'after_change'
    for item in data:
        if 'before_change' in item:
            item['before_change'] = fix_unicode(item['before_change'])
        if 'after_change' in item:
            item['after_change'] = fix_unicode(item['after_change'])
            print(item['after_change'])

    # Сохраняем изменения
    db.commit()


@router.post("/fix_unicode_in_database/")
async def fix_unicode_in_database_endpoint(json_data: str, db: Session = Depends(get_db)):
    fix_unicode_in_database(db, json_data)
    return {"message": "Unicode в базе данных исправлено успешно"}


# Функция для исправления Unicode-последовательностей
def fix_unicode(string):
    if "\\u" in string:
        parts = string.split(" ")
        fixed_parts = [part.encode().decode('unicode-escape') if "\\u" in part else part for part in parts]
        fixed_string = " ".join(fixed_parts)
        return fixed_string
    else:
        return string
