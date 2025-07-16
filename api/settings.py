from aiohttp import web
from aiohttp_apispec import (
    docs,
    request_schema,
    response_schema,
)
from config import logger
from docs import schems as sh
from functions import settings as func
import core
from api import validate

@docs(
    tags=["Settings"],
    summary="Получение профиля",
    description="Возвращает информацию о пользователе. Для доступа требуется Bearer-токен в заголовке Authorization",
    responses={
        200: {"description": "Профиль успешно получен", "schema": sh.UserProfileSchema},
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
async def info(request: web.Request) -> web.Response:
    try:
        user_id = await core.check_authorization(request)
        if not isinstance(user_id, str):
            return user_id
        
        res = await func.info(user_id)
        
        return web.json_response(res, status=200)
    except Exception as e:
        logger.error("profile error: ", e)
        return web.Response(status=500, text=str(e))
    
    
@docs(
    tags=["Settings"],
    summary="Изменение почты",
    description="Изменяет почту. Для доступа требуется Bearer-токен в заголовке Authorization",
    responses={
        204: {"description": "Профиль успешно изменён"},
        400: {"description": "Отсутствует один из параметров", "schema": sh.Error400Schema},
        401: {"description": "Авторизация не выполнена"},
        409: {"description": "Новые логин или почта заняты", "schema": sh.AlreadyBeenTaken},
        422: {"description": "Переданный email не соответствует стандартам электронной почты"},
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
@request_schema(sh.UserEditSchema)
@validate.validate(validate.Profile_patch)
async def set_email(request: web.Request, parsed : validate.Profile_patch) -> web.Response:
    try:
        user_id = await core.check_authorization(request)
        if not isinstance(user_id, str):
            return user_id
        
        email_new = parsed.email
        return await func.set_email(user_id, email_new)
    except Exception as e:
        logger.error("profile error: ", e)
        return web.Response(status=500, text=str(e))