from aiohttp import web
from aiohttp_apispec import (
    docs,
    request_schema,
    response_schema,
)
from config import logger
from docs import schems as sh
from functions import clubs as func
import core
from api import validate

@docs(
    tags=["Clubs"],
    summary="Получение списка клубов",
    description="Возвращает список клубов с учётом настроек.",
    responses={
        200: {"description": "Клубы успешно получены", "schema": sh.ScheduleItemSchema(many=True)},
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
@request_schema(sh.ClubsListSchema)
@validate.validate(validate.Clubs_list)
async def info(request: web.Request, parsed : validate.Clubs_list) -> web.Response:
    try:
        user_id = await core.check_authorization(request)
        if not isinstance(user_id, int):
            return user_id
        
        res = await func.info(user_id, parsed.type, parsed.offset, parsed.limit)
        
        return web.json_response(res, status=200)
    except Exception as e:
        logger.error("profile error: ", e)
        return web.Response(status=500, text=str(e))
    