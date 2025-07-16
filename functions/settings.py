from database.database import Database
from aiohttp import web
from functions import mail
from core import generate_unique_code

async def info(user_id:int):
    async with Database() as db:
        res = await db.execute("SELECT login, email, name, surname, telegram_id FROM users WHERE id=$1", (user_id,))
    return res

async def set_login(user_id:int, loign_new:str):
    async with Database() as db:
        res = await db.execute("SELECT 1 FROM users WHERE login = $1", (loign_new,))
        if res:
            return web.json_response({"name": "login", "error": "The login has already been registered"}, status=409)
        await db.execute("UPDATE users SET login=$2 WHERE id=$1", (user_id, loign_new))
    return web.Response(status=204)

async def set_email(user_id:int, email_new:str):
    async with Database() as db:
        res = await db.execute("SELECT 1 FROM users WHERE email = $1", (email_new,))
        if res:
            return web.json_response({"name": "email", "error": "The email has already been registered"}, status=409)
        await db.execute("DELETE FROM new_email WHERE user_id = $1", (user_id,))
        token = generate_unique_code()
        await mail.send_email_edit()
        await db.execute("INSERT INTO new_email (token, user_id, new_email) VALUES ($1, $2, $3)", (token, user_id, email_new))
    return web.Response(status=204)