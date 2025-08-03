from database.database import Database
import json
from datetime import date, datetime, timedelta

async def info(user_id: int, date: date) -> dict:
    """
    Получение расписания на определённый день с учётом замен и занятий клубов.
    
    :param user_id: ID пользователя
    :param date_str: Дата в формате 'YYYY-MM-DD'
    :return: Расписание на указанный день
    """
    try:
        schedule = []
        
        async with Database() as db:
            user = await db.execute("SELECT * FROM users WHERE id = $1", (user_id,))
            
            lesson_times = await db.execute_all("SELECT * FROM lesson_time WHERE day_number = $1", (date.weekday()+1,))
            lesson_times_special = await db.execute_all("SELECT * FROM lesson_time_special WHERE date = $1", (date,))
            
            lessons = await db.execute_all("SELECT * FROM lessons WHERE day_number = $1 AND class_number = $2 AND class_letter = $3", 
                                           (date.weekday()+1, user['class_number'], user['class_letter']))
            lesson_substitutions = await db.execute_all("SELECT * FROM lesson_substitutions WHERE date = $1 AND class_number = $2 AND class_letter = $3", 
                                                        (date, user['class_number'], user['class_letter']))
            
        for lesson_time in lesson_times:
            for lesson_time_special in lesson_times_special:
                if lesson_time['lesson_number'] == lesson_time_special['lesson_number']:
                    lesson_time = lesson_time_special
                    break
                
            index = next((idx for idx, d in enumerate(lesson_substitutions) if d.get('lesson_number') == lesson_time['lesson_number']), None)
            if index is None:
                index = next((idx for idx, d in enumerate(lessons) if d.get('lesson_number') == lesson_time['lesson_number']), None)
                if index is not None:
                    lesson_time.update(lessons[index])
                    lesson_time["replacement"] = False
            else:
                lesson_time["replacement"] = True
                lesson_time.update(lesson_substitutions[index])
            
            lesson_time.pop('id', None), lesson_time.pop('day_number', None), lesson_time.pop('date', None)
            lesson_time.pop('class_number', None), lesson_time.pop('class_letter', None)
            schedule.append(lesson_time)
                
        
        return schedule
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }