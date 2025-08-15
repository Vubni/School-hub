import os
from aiohttp import web
from aiohttp_apispec import (
    setup_aiohttp_apispec,
    validation_middleware
)
import aiohttp_cors
from config import logger
import asyncio
from api import (auth, settings, schedule, clubs, others, achievements, events, olympiads)

from database.functions import init_db


async def handle_get_file(request: web.Request) -> web.Response:
    # Определяем путь к статическим файлам
    static_dir = "static"
    path = request.match_info['path']
    
    # Создаем безопасный путь и проверяем выход за пределы директории
    safe_path = os.path.normpath(path).lstrip('/')
    full_path = os.path.join(static_dir, safe_path)
    abs_static = os.path.abspath(static_dir)
    abs_target = os.path.abspath(full_path)
    
    # Защита от path traversal
    if not abs_target.startswith(abs_static):
        return web.HTTPNotFound()
    
    # Если файл существует - отдаем его
    if os.path.isfile(abs_target):
        return web.FileResponse(abs_target)
    
    # Проверяем наличие расширения у запрошенного пути
    last_part = safe_path.split('/')[-1] if safe_path else ""
    if '.' in last_part:
        return web.HTTPNotFound()
    
    # Отдаем index.html для SPA роутинга
    index_path = os.path.join(static_dir, "index.html")
    if os.path.isfile(index_path):
        return web.FileResponse(index_path)
    
    return web.HTTPNotFound()


if __name__ == "__main__":
    asyncio.run(init_db())
    
    app = web.Application()

    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods=["GET", "POST", "OPTIONS", "PATCH", "DELETE"]
        )
    })
    
    setup_aiohttp_apispec(
        app,
        title="API doc",
        version="v1",
        url="/swagger.json",
        swagger_path="/doc",
        security_definitions={
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "Bearer token authorization"
            }
        }
    )

    prefix = "/"
    routes = [
        # web.post(prefix + 'reg', auth.register),
        web.post(prefix + 'auth', auth.auth),
        web.post(prefix + 'email', auth.email_verify),
        
        web.get(prefix + 'schedule', schedule.info),
        
        web.get(prefix + 'clubs/list', clubs.info),
        web.get(prefix + 'clubs/get', clubs.get),
        web.get(prefix + 'clubs/administrations', clubs.administrations),
        web.post(prefix + 'clubs/new', clubs.new),
        web.post(prefix + 'clubs/check_title', clubs.check_title),
        web.post(prefix + 'clubs/join', clubs.join_club),
        web.post(prefix + 'clubs/leave', clubs.leave_club),
        web.patch(prefix + 'clubs/edit', clubs.edit),
        web.delete(prefix + 'clubs/del', clubs.delete),

        # web.get(prefix + 'clubs/office/list', clubs.office_list),
        # web.post(prefix + 'clubs/office/occupy', clubs.office_occupy),
        # web.get(prefix + 'clubs/office/my', clubs.office_my),
        # web.delete(prefix + 'clubs/office/free', clubs.office_free),

        web.get(prefix + "achievement/global", clubs.achievements_global),
        web.get(prefix + "achievement/local", clubs.achievements_local),

        web.get(prefix + 'settings/info', settings.info),
        web.post(prefix + 'settings/login/set', settings.set_login),
        web.post(prefix + 'settings/password/set', settings.set_password),
        web.post(prefix + 'settings/email/set', settings.set_email),
        web.get(prefix + 'settings/telegram/connect', settings.telegram_connect),
        web.delete(prefix + 'settings/telegram/out', settings.telegram_out),

        web.get(prefix + 'news/achievements', achievements.get),
        web.get(prefix + 'news/events', events.get),
        web.get(prefix + 'news/olympiads', olympiads.get),

        web.get(prefix + 'teachers', others.teachers),
        
        web.get('/{path:.*}', handle_get_file)
    ]
    
    for route in routes:
        cors.add(app.router.add_route(route.method, route.path, route.handler))

    app.middlewares.append(validation_middleware)
    
    logger.info("Запуск сервера. . .")
    web.run_app(
        app,
        host=os.environ.get('INSTANCE_HOST', 'localhost'),
        port=int(os.environ.get('PORT', 8080))
    )