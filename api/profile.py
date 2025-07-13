from aiohttp import web
from aiohttp_apispec import (
    docs,
    request_schema,
    response_schema,
)
from config import logger
from docs import schems as sh
from functions import auth as func_db
import core
from api import validate

@docs(
    tags=["Profile"],
    summary="Получение профиля",
    description="Возвращает информацию о пользователе. Если профиль не верифицирован то будет возвращено лишь {'verified': false}. Для доступа требуется Bearer-токен в заголовке Authorization",
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
async def profile_get(request: web.Request) -> web.Response:
    try:
        email = await core.check_authorization(request)
        if not isinstance(email, str):
            return email
        
        res = await func_db.profile_get(email)
        if not res["verified"]:
            return web.json_response({"verified": False}, status=200)
        
        return web.json_response(res, status=200)
    except Exception as e:
        logger.error("profile error: ", e)
        return web.Response(status=500, text=str(e))
    
    
@docs(
    tags=["Profile"],
    summary="Удаление профиля",
    description="Удаляет профиль. Для доступа требуется Bearer-токен в заголовке Authorization",
    responses={
        204: {"description": "Профиль успешно удалён"},
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
async def profile_delete(request: web.Request) -> web.Response:
    try:
        email = await core.check_authorization(request)
        if not isinstance(email, str):
            return email
        
        return await func_db.profile_delete(email)
    except Exception as e:
        logger.error("profile error: ", e)
        return web.Response(status=500, text=str(e))
    
    
@docs(
    tags=["Profile"],
    summary="Изменение профиля",
    description="Изменяет профиль. Для доступа требуется Bearer-токен в заголовке Authorization",
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
async def profile_patch(request: web.Request, parsed : validate.Profile_patch) -> web.Response:
    try:
        email = await core.check_authorization(request)
        if not isinstance(email, str):
            return email
        
        email_new = parsed.email
        first_name = parsed.first_name
        password_old = parsed.password_old
        password_new = parsed.password_new
        
        return await func_db.profile_edit(email, email_new, first_name, password_old, password_new)
    except Exception as e:
        logger.error("profile error: ", e)
        return web.Response(status=500, text=str(e))