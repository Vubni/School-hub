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
    description="Возвращает список клубов с учётом настроек.\nТип клубов - my, all, top. all - все клубы, где я не участвую, my - мои клубы, top - топ клубов\nДля доступа требуется Bearer-токен в заголовке Authorization",
    responses={
        200: {"description": "Клубы успешно получены", "schema": sh.ClubSchema(many=True)},
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
        
        res = await func.list(user_id, parsed.type, parsed.offset, parsed.limit)
        
        return web.json_response(res, status=200)
    except Exception as e:
        logger.error("profile error: ", e)
        return web.Response(status=500, text=str(e))
    
@docs(
    tags=["Clubs"],
    summary="Получить информацию о клубе",
    description="Возвращает информацию о клубе\ntelegram_url возвращается только если человек состоит в клубе.\nДля доступа требуется Bearer-токен в заголовке Authorization",
    responses={
        200: {"description": "Клуб успешно получен", "schema": sh.ClubGetReturnSchema},
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
@request_schema(sh.ClubGetSchema)
@validate.validate(validate.Club_info)
async def get(request: web.Request, parsed : validate.Club_info) -> web.Response:
    try:
        user_id = await core.check_authorization(request)
        if not isinstance(user_id, int):
            return user_id
        
        res = await func.get(user_id, parsed.club_id)
        
        return web.json_response(res, status=200)
    except Exception as e:
        logger.error("profile error: ", e)
        return web.Response(status=500, text=str(e))
    
    
@docs(
    tags=["Clubs"],
    summary="Создание нового клуба",
    description="""Создаёт новый клуб
    
title - название клуба, обязательно
description - описание клуба, обязательно
administration - id направления, обязательно
max_members_counts - макисмальное количество участников, необязательно, по умолчанию 0 = бесконечность (значение либо 0, либо >4)
class_limit_min - минимальный класс для участия, необязательно, по умолчанию 1 (диапозон 1-11)
class_limit_max - максимальный класс для участия, необязательно, по умолчанию 1 (диапозон 1-11)
telegram_url - ссылка на телеграм группу/канал, необязательно, по умолчанию - null.
\nДля доступа требуется Bearer-токен в заголовке Authorization""",
    responses={
        201: {"description": "Клуб успешно создан", "schema": sh.ClubGetReturnSchema},
        400: {"description": "Отсутствует один из параметров", "schema": sh.Error400Schema},
        401: {"description": "Авторизация не выполнена"},
        409: {"description": "Новые логин или почта заняты", "schema": sh.AlreadyBeenTaken},
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
@request_schema(sh.ClubNewSchema)
@validate.validate(validate.Club_new)
async def new(request: web.Request, parsed : validate.Club_new) -> web.Response:
    try:
        user_id = await core.check_authorization(request)
        if not isinstance(user_id, int):
            return user_id
        
        result = await func.create(user_id, parsed.title, parsed.description,
                             parsed.administration, parsed.max_members_counts,
                             parsed.class_limit_min, parsed.class_limit_max,
                             parsed.telegram_url)
        
        if isinstance(result, dict):
            return web.json_response(result, status=200)
        else:
            return result
    except Exception as e:
        logger.error("profile error: ", e)
        return web.Response(status=500, text=str(e))
    
@docs(
    tags=["Clubs"],
    summary="Проверка уникальности названия клуба",
    description="Проверка уникальности названия клуба\nДля доступа требуется Bearer-токен в заголовке Authorization",
    responses={
        204: {"description": "Название не занято"},
        400: {"description": "Отсутствует один из параметров", "schema": sh.Error400Schema},
        401: {"description": "Авторизация не выполнена"},
        409: {"description": "Новые логин или почта заняты", "schema": sh.AlreadyBeenTaken},
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
@request_schema(sh.CheckTitleSchema)
@validate.validate(validate.Check_title)
async def check_title(request: web.Request, parsed : validate.Check_title) -> web.Response:
    try:
        user_id = await core.check_authorization(request)
        if not isinstance(user_id, int):
            return user_id
        
        result = await func.check_title(parsed.title)
        
        if isinstance(result, dict):
            return web.json_response(result, status=200)
        else:
            return result
    except Exception as e:
        logger.error("profile error: ", e)
        return web.Response(status=500, text=str(e))
    
    
@docs(
    tags=["Clubs"],
    summary="Направления клубов",
    description="Получение направления клубов\nДля доступа требуется Bearer-токен в заголовке Authorization",
    responses={
        200: {"description": "Направления клубов", "schema": sh.AdministrationListSchema(many=True)},
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
async def administrations(request: web.Request) -> web.Response:
    try:
        user_id = await core.check_authorization(request)
        if not isinstance(user_id, int):
            return user_id
        
        result = await func.administrations()
        
        return web.json_response(result, status=200)
    except Exception as e:
        logger.error("profile error: ", e)
        return web.Response(status=500, text=str(e))
    
@docs(
    tags=["Clubs"],
    summary="Присоединиться в клуб",
    description="Присоединиться в клуб\nДля доступа требуется Bearer-токен в заголовке Authorization",
    responses={
        200: {"description": "Информация о клубе (аналогично clubs/get)", "schema": sh.ClubGetReturnSchema},
        400: {"description": "Отсутствует один из параметров", "schema": sh.Error400Schema},
        401: {"description": "Авторизация не выполнена"},
        403: {"description": "В клубе максимальное количество участников"},
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
@request_schema(sh.ClubJoinSchema)
@validate.validate(validate.Club_join)
async def join_club(request: web.Request, parsed : validate.Club_join) -> web.Response:
    try:
        user_id = await core.check_authorization(request)
        if not isinstance(user_id, int):
            return user_id
        
        result = await func.join_club(user_id, parsed.club_id)
        
        if isinstance(result, dict):
            return web.json_response(result, status=200)
        else:
            return result
    except Exception as e:
        logger.error("profile error: ", e)
        return web.Response(status=500, text=str(e))
    
@docs(
    tags=["Clubs"],
    summary="Покинуть клуб",
    description="Покинуть клуб\nДля доступа требуется Bearer-токен в заголовке Authorization",
    responses={
        200: {"description": "Покинуть клуб", "schema": sh.ClubGetReturnSchema},
        400: {"description": "Отсутствует один из параметров", "schema": sh.Error400Schema},
        401: {"description": "Авторизация не выполнена"},
        403: {"description": "Единственный администратор не может покинуть клуб."},
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
@request_schema(sh.ClubJoinSchema)
@validate.validate(validate.Club_join)
async def leave_club(request: web.Request, parsed : validate.Club_join) -> web.Response:
    try:
        user_id = await core.check_authorization(request)
        if not isinstance(user_id, int):
            return user_id
        
        result = await func.leave_club(user_id, parsed.club_id)
        
        if isinstance(result, dict):
            return web.json_response(result, status=200)
        else:
            return result
    except Exception as e:
        logger.error("profile error: ", e)
        return web.Response(status=500, text=str(e))