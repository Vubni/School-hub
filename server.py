import os
from aiohttp import web
from aiohttp_apispec import (
    setup_aiohttp_apispec,
    validation_middleware
)
import aiohttp_cors
from config import logger
import asyncio
from api import (auth, settings, schedule, clubs)

from database.functions import init_db

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
        # web.patch(prefix + 'clubs/edit', clubs.info),
        web.delete(prefix + 'clubs/del', clubs.delete),

        web.get(prefix + 'settings/info', settings.info),
        web.post(prefix + 'settings/login/set', settings.set_login),
        web.post(prefix + 'settings/password/set', settings.set_password),
        web.post(prefix + 'settings/email/set', settings.set_email),
        web.get(prefix + 'settings/telegram/connect', settings.telegram_connect),
        web.delete(prefix + 'settings/telegram/out', settings.telegram_out),
        
        # web.get('/{path:.*}', handle_get_file)
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