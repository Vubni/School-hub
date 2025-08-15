from aiohttp import web
from aiohttp_apispec import (
    docs,
    request_schema,
    response_schema,
)
from config import logger
from docs import schems as sh
from functions import achievements as func
import core
from api import validate
from dateutil import parser
from datetime import date

@docs(
    tags=["Achievements"],
    summary="Получение списка достижений учеников лицея",
    description="Получение списка достижений учеников лицея",
    responses={
        200: {"description": "Список достижений учеников лицея", "schema": sh.AchievementsSchema(many=True)},
        400: {"description": "Отсутствует один из параметров", "schema": sh.Error400Schema},
        401: {"description": "Авторизация не выполнена"},
        500: {"description": "Server-side error (Ошибка на стороне сервера)"}
    },
    parameters=[{
        'in': 'header',
        'name': 'Authorization',
        'schema': {'type': 'string', 'format': 'Bearer'},
        'required': True,
        'description': 'Bearer-токен для аутентификации'
    }]
)
async def get(request: web.Request) -> web.Response:
    try:
        user_id = await core.check_authorization(request)
        if not isinstance(user_id, int):
            return user_id
        
        res = await func.get()
        
        return web.json_response(res, status=200)
    except Exception as e:
        logger.error("profile error: ", e)
        return web.Response(status=500, text=str(e))
    