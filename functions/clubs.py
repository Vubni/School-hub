from database.database import Database
import json
from datetime import date, datetime, timedelta
from aiohttp import web

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
                    """SELECT c.id, c.title, c.max_members_counts, 
                          c.class_limit_min, c.class_limit_max
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
                    """SELECT c.id, c.title, c.max_members_counts, 
                          c.class_limit_min, c.class_limit_max
                    FROM clubs c
                    INNER JOIN club_members cm ON c.id = cm.club_id
                    WHERE cm.user_id = $1
                    LIMIT $2 OFFSET $3""",
                    (user_id, limit, offset)
                )
                
            elif type == "top":
                clubs = await db.execute_all(
                    """SELECT id, title, max_members_counts, 
                          class_limit_min, class_limit_max 
                    FROM clubs 
                    ORDER BY xp DESC 
                    LIMIT $1 OFFSET $2""",
                    (limit, offset)
                )
                
            else:
                return {
                    "status": "error",
                    "message": f"Unknown type: {type}. Valid options: all, my, top"
                }
            
            for club in clubs:
                members_count = (await db.execute("SELECT COUNT(*) as count FROM club_members WHERE club_id=$1", (club["id"],)))["count"]
                club["members_count"] = members_count

        
        return clubs
        
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
            club = await db.execute("SELECT * FROM clubs WHERE id = $1", (club_id,))
            is_participant = await db.execute("SELECT * FROM club_members WHERE user_id=$1 AND club_id=$2", (user_id, club_id))
            if is_participant:
                club["participant"] = True
                club["admin"] = is_participant["admin"]
            else:
                club["participant"] = False
                del club["telegram_url"]
            res = await db.execute("SELECT title FROM administrations WHERE id = $1", (club["administration"],))
            club["administration"] = res['title'] if res else "Unknown"
            members_count = (await db.execute("SELECT COUNT(*) as count FROM club_members WHERE club_id=$1", (club_id,)))["count"]
            club["members_count"] = members_count
        
        return club
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
        
async def create(user_id: int, title: str, description: str, administration: int, max_members_counts: int, class_limit_min: int, class_limit_max: int, telegram_url: str) -> dict:
    """
    Создание нового клуба
    
    :param user_id: ID создателя клуба
    :param title: Название клуба
    :param description: Описание клуба
    :param administration: Список администраторов клуба
    :param max_members_counts: Максимальное количество участников
    :param class_limit_min: Минимальное количество участников для занятия
    :param class_limit_max: Максимальное количество участников для занятия
    :param telegram_url: URL телеграм-канала клуба
    :return: Словарь с информацией о созданном клубе или сообщением об ошибке
    """
    try:
        async with Database() as db:
            exists = await db.execute("SELECT 1 FROM clubs WHERE title = $1", (title,))
            if exists:
                return web.json_response({"name": "login", "message": "login is already occupied"}, status=409)
            
            await db.execute("INSERT INTO clubs (title, description, administration, max_members_counts, class_limit_min, class_limit_max, telegram_url) VALUES ($1, $2, $3, $4, $5, $6, $7)",
                             (title, description, administration, max_members_counts, class_limit_min, class_limit_max, telegram_url))
            result = await db.execute("SELECT * FROM clubs WHERE title = $1", (title,))
            await db.execute("INSERT INTO club_members (club_id, user_id, admin) VALUES ($2, $1, $3)", (user_id, result['id'], True))
            result["participant"] = True
            result["admin"] = True
            res = await db.execute("SELECT title FROM administrations WHERE id = $1", (administration,))
            result["administration"] = res['title'] if res else "Unknown"
            return result
    except Exception as e:
        return {"status": "error", "message": str(e)}
        
async def check_title(title: str) -> dict:
    """
    Проверка уникальности названия клуба
    
    :param title: Название клуба
    :return: Словарь с результатом проверки
    """
    try:
        async with Database() as db:
            exists = await db.execute("SELECT 1 FROM clubs WHERE title = $1", (title,))
            if exists:
                return web.json_response({"name": "login", "message": "login is already occupied"}, status=409)
        
        return {}
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
        
async def administrations() -> dict:
    """
    Проверка уникальности названия клуба
    
    :param title: Название клуба
    :return: Словарь с результатом проверки
    """
    try:
        async with Database() as db:
            result = await db.execute_all("SELECT * FROM administrations")
        return result
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
        
async def join_club(user_id: int, club_id: int) -> dict:
    """
    Проверка уникальности названия клуба
    
    :param title: Название клуба
    :return: Словарь с результатом проверки
    """
    try:
        async with Database() as db:
            is_member = await db.execute("SELECT 1 FROM club_members WHERE user_id=$1 AND club_id=$2", (user_id, club_id))
            if is_member:
                return web.json_response({"name": "already join", "message": "already join"}, status=403)
            
            max_members = (await db.execute("SELECT max_members_counts FROM clubs WHERE id = $1", (club_id,)))["max_members_counts"]
            if max_members > 0:
                count_participants = (await db.execute("SELECT COUNT(*) as count FROM club_members WHERE club_id=$1", (club_id,)))["count"]
                if count_participants >= max_members:
                    return web.json_response({"name": "max_members_counts", "message": "The group already has the maximum number of members"}, status=403)
        
            await db.execute("INSERT INTO club_members (club_id, user_id) VALUES ($2, $1)", (user_id, club_id))
            result = await db.execute("SELECT * FROM clubs WHERE id = $1", (club_id,))
            result["participant"] = True
            res = await db.execute("SELECT title FROM administrations WHERE id = $1", (result["administration"],))
            result["administration"] = res['title'] if res else "Unknown"
        return result
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
        
async def leave_club(user_id: int, club_id: int) -> dict:
    """
    Проверка уникальности названия клуба
    
    :param title: Название клуба
    :return: Словарь с результатом проверки
    """
    try:
        async with Database() as db:
            count_admins = (await db.execute("SELECT COUNT(*) as count FROM club_members WHERE club_id=$1 AND admin=true", (club_id,)))["count"]
            if count_admins == 1:
                is_admin = await db.execute("SELECT 1 FROM club_members WHERE user_id=$1 AND club_id=$2 AND admin=true", (user_id, club_id))
                if is_admin:
                    return web.json_response({"name": "count_admins", "message": "The only administrator cannot leave the club."}, status=403)
            
            await db.execute("DELETE FROM club_members WHERE user_id=$1 AND club_id=$2", (user_id, club_id))
            result = await db.execute("SELECT * FROM clubs WHERE id = $1", (club_id,))
            result["participant"] = False
            res = await db.execute("SELECT title FROM administrations WHERE id = $1", (result["administration"],))
            result["administration"] = res['title'] if res else "Unknown"
        return result
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
    
async def delete(user_id, club_id):
    try:
        async with Database() as db:
            res = await db.execute("SELECT 1 FROM users WHERE user_id=$1 and admin=true", (user_id,))
            if not res:
                return web.json_response({"name": "user_id", "message": "User is not admin."}, status=401)
            await db.execute("DELETE FROM clubs WHERE club_id=$1", (club_id,))
        return web.Response(status=200)
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }