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
        if not isinstance(user_id, int):
            return user_id
        
        res = await func.info(user_id)
        
        return web.json_response(res, status=200)
    except Exception as e:
        logger.error("profile error: ", e)
        return web.Response(status=500, text=str(e))
    
    
@docs(
    tags=["Settings"],
    summary="Изменение логина",
    description="Изменяет логин. Для доступа требуется Bearer-токен в заголовке Authorization",
    responses={
        204: {"description": "Логин успешно изменён"},
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
@request_schema(sh.LoginEditSchema)
@validate.validate(validate.Login_patch)
async def set_login(request: web.Request, parsed : validate.Login_patch) -> web.Response:
    try:
        user_id = await core.check_authorization(request)
        if not isinstance(user_id, int):
            return user_id
        
        login_new = parsed.login
        return await func.set_login(user_id, login_new)
    except Exception as e:
        logger.error("profile error: ", e)
        return web.Response(status=500, text=str(e))
    
    
@docs(
    tags=["Settings"],
    summary="Изменение почты",
    description="Изменяет почту. Для доступа требуется Bearer-токен в заголовке Authorization",
    responses={
        204: {"description": "Почта успешно изменена"},
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
@request_schema(sh.EmailEditSchema)
@validate.validate(validate.Email_patch)
async def set_email(request: web.Request, parsed : validate.Email_patch) -> web.Response:
    try:
        user_id = await core.check_authorization(request)
        if not isinstance(user_id, int):
            return user_id
        
        email_new = parsed.email
        return await func.set_email(user_id, email_new)
    except Exception as e:
        logger.error("profile error: ", e)
        return web.Response(status=500, text=str(e))
    
@docs(
    tags=["Settings"],
    summary="Изменение пароля",
    description="Изменяет пароль. Для доступа требуется Bearer-токен в заголовке Authorization",
    responses={
        204: {"description": "Пароль успешно изменён"},
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
@request_schema(sh.PasswordEditSchema)
@validate.validate(validate.Password_patch)
async def set_password(request: web.Request, parsed : validate.Password_patch) -> web.Response:
    try:
        user_id = await core.check_authorization(request)
        if not isinstance(user_id, int):
            return user_id
        
        return await func.set_password(user_id, parsed.password_old, parsed.password_new)
    except Exception as e:
        logger.error("profile error: ", e)
        return web.Response(status=500, text=str(e))
    
    
@docs(
    tags=["Settings"],
    summary="Отвязка Telegram аккаунта",
    description="Отвязка Telegram аккаунта. Для доступа требуется Bearer-токен в заголовке Authorization",
    responses={
        204: {"description": "Telegram аккаунт успешно отвязан"},
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
async def telegram_out(request: web.Request) -> web.Response:
    try:
        user_id = await core.check_authorization(request)
        if not isinstance(user_id, int):
            return user_id
        
        return await func.telegram_out(user_id)
    except Exception as e:
        logger.error("profile error: ", e)
        return web.Response(status=500, text=str(e))
    
@docs(
    tags=["Settings"],
    summary="Получение ссылки для привязки Telegram аккаунта",
    description="Получение ссылки для привязки Telegram аккаунта. Для доступа требуется Bearer-токен в заголовке Authorization",
    responses={
        204: {"description": "Telegram аккаунт успешно привязан", "schema": sh.TelegramConnectSchema},
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
async def telegram_connect(request: web.Request) -> web.Response:
    try:
        user_id = await core.check_authorization(request)
        if not isinstance(user_id, int):
            return user_id
        auth_header = request.headers.get('Authorization')
        token = auth_header.split()[1]
        return web.json_response({"url": f"https://t.me/schoolhub_ru_bot?start=connect_{token}"}, status=200)
        # return await func.telegram_sign(user_id)
    except Exception as e:
        logger.error("profile error: ", e)
        return web.Response(status=500, text=str(e))