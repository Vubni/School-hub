from database.database import Database
import json
from datetime import date, datetime, timedelta

async def list(user_id: int, type: str, offset: int, limit: int) -> dict:
    """
    Получение расписания на определённый день с учётом замен и занятий клубов.
    
    :param user_id: ID пользователя
    :param date_str: Дата в формате 'YYYY-MM-DD'
    :return: Расписание на указанный день
    """
    try:
        async with Database() as db:
            clubs = await db.execute_all("SELECT * FROM lesson_time_special WHERE date = $1" \
            "LIMIT $1 OFFSET $2", (limit, offset))
            
        return clubs
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }