from database.database import Database
import json
from datetime import date, datetime, timedelta

async def list(user_id: int, type: str, offset: int, limit: int) -> dict:
    """
    Получение списка клубов по указанному типу выборки
    
    :param user_id: ID пользователя
    :param type: Тип выборки (all, my, top)
    :param offset: Смещение для пагинации
    :param limit: Лимит записей
    :return: Словарь со списком клубов или сообщением об ошибке
    """
    try:
        async with Database() as db:
            # Обработка разных типов запросов
            if type == "all":
                clubs = await db.execute_all(
                    """SELECT c.* 
                    FROM clubs c
                    WHERE NOT EXISTS (
                        SELECT 1 FROM club_members 
                        WHERE club_id = c.id AND user_id = $1
                    )
                    LIMIT $2 OFFSET $3""",
                    (user_id, limit, offset)
                )
                
            elif type == "my":
                clubs = await db.execute_all(
                    """SELECT c.* 
                    FROM clubs c
                    INNER JOIN club_members cm ON c.id = cm.club_id
                    WHERE cm.user_id = $1
                    LIMIT $2 OFFSET $3""",
                    (user_id, limit, offset)
                )
                
            elif type == "top":
                clubs = await db.execute_all(
                    "SELECT * FROM clubs ORDER BY xp DESC LIMIT $1 OFFSET $2",
                    (limit, offset)
                )
                
            else:
                return {
                    "status": "error",
                    "message": f"Unknown type: {type}. Valid options: all, my, top"
                }
        
        return {"status": "success", "data": clubs}
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
        

async def get(user_id: int, club_id: int) -> dict:
    """
    Получение информации о клубе по его ID
    
    :param user_id: ID пользователя
    :param club_id: ID клуба
    :return: Словарь с информацией о клубе или сообщением об ошибке
    """
    try:
        async with Database() as db:
            club = await db.execute_one(
                "SELECT * FROM clubs WHERE id = $1",
                (club_id,)
            )
            
            if not club:
                return {
                    "status": "error",
                    "message": f"Club with ID {club_id} not found"
                }
        
        return {"status": "success", "data": club}
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }