from aiohttp import web
from aiohttp_apispec import (
    docs,
    request_schema,
    response_schema,
)
from config import logger
from docs import schems as sh
from functions import auth as func
from api import validate
import core
from functions import mail
from database.database import Database

@docs(
    tags=["Auth"],
    summary="Авторизация пользователя",
    description="Получение токена авторизации",
    responses={
        200: {"description": "Авторизация успешно выполнена", "schema": sh.TokenResponseSchema},
        400: {"description": "Отсутствует один из параметров или ограничения параметра не выполнены", "schema": sh.Error400Schema},
        401: {"description": "Логин или почта не зарегистрированы"},
        500: {"description": "Server-side error (Ошибка на стороне сервера)"}
    }
)
@request_schema(sh.UserAuthSchema)
@validate.validate(validate.Auth)
async def auth(request: web.Request, parsed : validate.Auth) -> web.Response:
    try:
        identifier = parsed.identifier
        password = parsed.password
        
        code = await func.auth(identifier, password)
        return code
    except Exception as e:
        logger.error("auth error: ", e)
        return web.Response(status=500, text=str(e))
    
@docs(
    tags=["Auth"],
    summary="Верификация email",
    description="Подтверждает почту. Для доступа требуется Bearer-токен в заголовке Authorization",
    responses={
        204: {"description": "Почта успешно подтверждена"},
        400: {"description": "Код авторизации не передан", "schema": sh.Error400Schema},
        401: {"description": "Код подтверждения неверный"},
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
async def email_verify(request: web.Request) -> web.Response:
    try:
        email = await core.check_authorization(request)
        if not isinstance(email, str):
            return email
        
        try:
            await func.verify_email(email)
            return web.Response(status=204)
        except:
            return web.Response(status=500)
    except Exception as e:
        logger.error("profile error: ", e)
        return web.Response(status=500, text=str(e))
    

@docs(
    tags=["Auth"],
    summary="Получение ссылки для авторизации через Telegram аккаунт",
    description="Получение ссылки для авторизации через Telegram аккаунт.",
    responses={
        204: {"description": "Ссылка на привязку Telegram аккаунта", "schema": sh.TelegramAuthSchema},
        401: {"description": "Авторизация не выполнена"},
        500: {"description": "Server-side error (Ошибка на стороне сервера)"}
    }
)
async def telegram_url(request: web.Request) -> web.Response:
    try:
        token = core.generate_unique_code()
        return web.json_response({"url": f"https://t.me/schoolhub_ru_bot?start=auth_{token}", "token": token}, status=200)
    except Exception as e:
        logger.error("profile error: ", e)
        return web.Response(status=500, text=str(e))
    
@docs(
    tags=["Auth"],
    summary="Проверка прошла ли авторизация через Telegram успешно",
    description="Проверка прошла ли авторизация через Telegram успешно.",
    responses={
        200: {"description": "Авторизация через Telegram аккаунт выполнена", "schema": sh.TokenResponseSchema},
        400: {"description": "Код авторизации не передан", "schema": sh.Error400Schema},
        401: {"description": "Авторизация ещё не выполнена"},
        500: {"description": "Server-side error (Ошибка на стороне сервера)"}
    }
)
@request_schema(sh.TokenResponseSchema)
@validate.validate(validate.Auth_telegram)
async def telegram(request: web.Request, parsed: validate.Auth_telegram) -> web.Response:
    try:
        res = await func.check_auth_token(parsed.token)
        return res
    except Exception as e:
        logger.error("profile error: ", e)
        return web.Response(status=500, text=str(e))
    
@docs(
    tags=["Auth"],
    summary="Отправка запроса на изменение пароля",
    description="Отправка запроса на изменение пароля.",
    responses={
        204: {"description": "Запрос на изменение пароля отправлен успешно"},
        400: {"description": "Код авторизации не передан", "schema": sh.Error400Schema},
        401: {"description": "Авторизация не выполнена"},
        422: {"description": "Почта и телеграм аккаунт не привязаны к пользователю"},
        500: {"description": "Server-side error (Ошибка на стороне сервера)"}
    }
)
@request_schema(sh.ForgotPasswordSchema)
@validate.validate(validate.Forgot_password)
async def forgot_password(request: web.Request, parsed: validate.Forgot_password) -> web.Response:
    try:
        res = await func.forgot_password(parsed.identifier, parsed.new_password)
        return res
    except Exception as e:
        logger.error("profile error: ", e)
        return web.Response(status=500, text=str(e))