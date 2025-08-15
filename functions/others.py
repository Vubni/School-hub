from database.database import Database
import json
from datetime import date, datetime, timedelta
from aiohttp import web

async def teachers():
    async with Database() as db:
        result = await db.execute_all("SELECT name, subject FROM teachers")
        for res in result:
            res["subject"] = (await db.execute("SELECT title FROM subjects WHERE id=$1", (res["subject"],)))["subject"]
    return result