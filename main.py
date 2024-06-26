import asyncio
import json
from datetime import time

import pandas as pd
import schedule
import telebot
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.dependencies.database.database import get_db
from app.models.item import Item
from app.routers.items_router import router as irouter
from app.routers.user_router import router as urouter
from app.routers.history_router import router as hrouter
from app.utils.send_excel import fetch_data, write_to_excel, write_to_excel_default

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(urouter)
app.include_router(irouter)
app.include_router(hrouter)


@app.get('/')
def root():
    return dict(message=f"all works")


TOKEN = "TOKEN"
bot = telebot.TeleBot(TOKEN)


def export_to_excel(db: Session):
    data = {}
    data['History'] = pd.read_sql_table('history', db.bind)
    data['Items'] = pd.read_sql_table('items', db.bind)
    data['Users'] = pd.read_sql_table('users', db.bind)

    data['History']['timestamp'] = data['History']['timestamp'].dt.tz_localize(None)

    file_path = 'database_export.xlsx'
    with pd.ExcelWriter(file_path) as writer:
        for sheet_name, df in data.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    with open(file_path, 'rb') as file:
        bot.send_document(IDIDID, file)

    print("Data exported to Excel file and sent to Telegram successfully")


def schedule_export():
    export_time = time(hour=18, minute=15)
    schedule.every().day.at(export_time.strftime('%H:%M')).do(lambda: export_to_excel(next(get_db())))


def send_files_to_telegram(db: Session):
    items = db.query(Item).order_by(Item.name).all()
    items_json = [{'name': item.name, 'price': item.price, 'quantity': item.quantity} for item in items]

    if items_json:
        write_to_excel(items_json)
        write_to_excel_default(items_json)
    files = ["price.xlsx", "price_default.xlsx"]
    for file in files:
        with open(file, 'rb') as f:
            bot.send_document(IDIDID, f)
    print("Files have been sent to Telegram successfully")


def schedule_send_files():
    schedule.every().day.at("03:00").do(lambda: send_files_to_telegram(next(get_db())))
    schedule.every().day.at("16:00").do(lambda: send_files_to_telegram(next(get_db())))


@app.on_event("startup")
async def startup_event():
    schedule_export()
    schedule_send_files()


async def run_schedule():
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)


@app.on_event("startup")
async def run_schedule_task():
    asyncio.create_task(run_schedule())
