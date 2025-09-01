from aiohttp import web
from aiohttp_apispec import (
    docs,
    request_schema,
    response_schema,
)
from config import logger
from docs import schems as sh
from functions import olympiads as func
import core
from api import validate
from dateutil import parser
from datetime import date

@docs(
    tags=["News"],
    summary="Получение списка будущих олимпиад",
    description="Получение списка будущих олимпиад",
    responses={
        200: {"description": "Список будущих олимпиад", "schema": sh.AchievementsSchema(many=True)},
        400: {"description": "Отсутствует один из параметров", "schema": sh.Error400Schema},
        401: {"description": "Авторизация не выполнена"},
        500: {"description": "Server-side error (Ошибка на стороне сервера)"}
    }
)
async def get(request: web.Request) -> web.Response:
    try:
        res = await func.get()
        
        return web.json_response(res, status=200)
    except Exception as e:
        logger.error("profile error: ", e)
        return web.Response(status=500, text=str(e))
    