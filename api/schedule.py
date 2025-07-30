from aiohttp import web
from aiohttp_apispec import (
    docs,
    request_schema,
    response_schema,
)
from config import logger
from docs import schems as sh
from functions import schedule as func
import core
from api import validate
from dateutil import parser
from datetime import date

@docs(
    tags=["Schedule"],
    summary="Получение расписания на определённый день",
    description="Возвращает расписание на определённую дату с учётом замен и занятий клубов.",
    responses={
        200: {"description": "Расписание успешно получено", "schema": sh.ScheduleItemSchema(many=True)},
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
@request_schema(sh.ScheduleGetSchema)
@validate.validate(validate.Schedule_get)
async def info(request: web.Request, parsed : validate.Schedule_get) -> web.Response:
    try:
        user_id = await core.check_authorization(request)
        if not isinstance(user_id, int):
            return user_id
        
        try:
            current_date = parser.parse(parsed.date).date()
        except ValueError:
            return web.json_response({
                "error": "Invalid date format",
                "received_date": parsed.date
            }, status=400)
        res = await func.info(user_id, current_date)
        
        return web.json_response(res, status=200)
    except Exception as e:
        logger.error("profile error: ", e)
        return web.Response(status=500, text=str(e))
    