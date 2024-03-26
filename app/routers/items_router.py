import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Dict, Union, Optional

from app.dependencies.database.database import get_db
from app.models.history import History
from app.models.item import Item
from app.models.user_model import User
from app.schemas.history_schemas import HistoryCreate
from app.schemas.item_schemas import ItemCreate, ItemOut, ItemUpdate, RetailSale, WholesaleSale
from app.dependencies.get_current_user import get_current_user

router = APIRouter(tags=['items'])


@router.post("/items/", response_model=List[ItemOut])
async def create_or_update_items(items: List[ItemCreate], db: Session = Depends(get_db),
                                 current_user: User = Depends(get_current_user)):
    created_or_updated_items = []
    for item in items:
        # Проверяем, существует ли товар с таким именем
        existing_item = db.query(Item).filter(Item.name == item.name).first()

        if existing_item:
            # Если товар уже существует, обновляем его количество и цену
            existing_item.quantity += item.quantity
            existing_item.price = item.price
            db.add(existing_item)
            db.commit()
            db.refresh(existing_item)
            created_or_updated_items.append(existing_item)
        else:
            # Если товара с таким именем еще нет, создаем новый
            db_item = Item(**item.dict())
            db.add(db_item)
            db.commit()
            db.refresh(db_item)
            created_or_updated_items.append(db_item)

    items_dict = [item.dict() for item in items]
    after_change_json = json.dumps(items_dict, ensure_ascii=False)

    title = f"{datetime.now().strftime('%d.%m.%Y')} | {current_user.username} Добавление товара | {datetime.now().strftime('%H:%M')}"
    history_entry = History(
        username=current_user.username,
        after_change=after_change_json,
        history_type="add",
        title=title
    )
    db.add(history_entry)
    db.commit()

    return created_or_updated_items


@router.get("/items/", response_model=List[ItemOut])
async def read_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    items = db.query(Item).offset(skip).limit(limit).all()
    return items


@router.get("/items/summary/", response_model=Dict[str, Union[int, float]])
async def get_items_summary(db: Session = Depends(get_db)):
    unique_items_count = db.query(Item).distinct(Item.name).count()

    total_items_count = db.query(func.sum(Item.quantity)).scalar() or 0

    total_price = db.query(func.sum(Item.price * Item.quantity)).scalar() or 0.0

    return {"unique_items_count": unique_items_count, "total_items_count": total_items_count,
            "total_price": total_price}


@router.get("/items/search/", response_model=List[ItemOut])
async def search_items_by_name(name: str, db: Session = Depends(get_db)):
    items = db.query(Item).filter(Item.name.like(f"%{name}%")).all()
    return items


@router.put("/items/{item_id}", response_model=ItemOut)
async def update_item(
        item_id: int,
        item_update: ItemUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        extra_info: Optional[str] = Body(None)  # Поле extra_info необязательно
):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    before_change = {
        "name": db_item.name,
        "price": db_item.price,
        "quantity": db_item.quantity
    }
    for key, value in item_update.dict().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)

    title = f"{datetime.now().strftime('%d.%m.%Y')} | {current_user.username} Изменения товара | {datetime.now().strftime('%H:%M')}"
    history_entry = History(
        username=current_user.username,
        before_change=json.dumps(before_change),
        after_change=json.dumps(item_update.dict()),
        history_type="update",
        extra_info=extra_info,  # Подставляем значение extra_info, если оно было передано
        title=title
    )
    db.add(history_entry)
    db.commit()

    return db_item


@router.post("/sell/wholesale/", response_model=HistoryCreate)
async def sell_wholesale(
        wholesale_sale: WholesaleSale,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    for item_data in wholesale_sale.items:
        db_item = db.query(Item).filter(Item.name == item_data.name).first()
        if not db_item:
            raise HTTPException(status_code=404, detail="Item not found")

        if db_item.quantity < item_data.quantity:
            raise HTTPException(status_code=400, detail="Not enough items in stock")

        db_item.quantity -= item_data.quantity
        db.commit()

        title = f"{datetime.now().strftime('%d.%m.%Y')} | {current_user.username} Оптовая продажа | {datetime.now().strftime('%H:%M')}"
        history_entry = History(
            username=current_user.username,
            buyer=wholesale_sale.buyer,
            extra_info=wholesale_sale.extra_info,
            before_change=json.dumps({}),  # Сериализуем пустой словарь в JSON-строку
            after_change=json.dumps({"name": db_item.name, "quantity": item_data.quantity, "price": db_item.price}),  # Сериализуем измененные данные в JSON-строку
            history_type="opt",
            title=title
        )
        db.add(history_entry)
        db.commit()

    return history_entry


@router.post("/sell/retail/", response_model=HistoryCreate)
async def sell_retail(
        retail_sale: RetailSale,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    for item_data in retail_sale.items:
        db_item = db.query(Item).filter(Item.name == item_data.name).first()
        if not db_item:
            raise HTTPException(status_code=404, detail="Item not found")

        if db_item.quantity < item_data.quantity:
            raise HTTPException(status_code=400, detail="Not enough items in stock")

        db_item.quantity -= item_data.quantity
        db.commit()

        title = f"{datetime.now().strftime('%d.%m.%Y')} | {current_user.username} Розничная продажа | {datetime.now().strftime('%H:%M')}"
        history_entry = History(
            username=current_user.username,
            buyer=None,
            extra_info=retail_sale.extra_info,
            before_change=json.dumps({}),  # Сериализуем пустой словарь в JSON-строку
            after_change=json.dumps({"name": db_item.name, "quantity": item_data.quantity, "price": db_item.price}),  # Сериализуем измененные данные в JSON-строку
            history_type="sale",
            title=title
        )
        db.add(history_entry)
        db.commit()

    return history_entry
