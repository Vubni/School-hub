from database.database import Database
import json
from datetime import date, datetime, timedelta
from aiohttp import web

async def get():
    async with Database() as db:
        result = await db.execute_all("SELECT title, description, image_path, date, url FROM news_achievements ORDER BY date DESC LIMIT 20")
    for res in result:
        res["date"] = str(res["date"])
    return result