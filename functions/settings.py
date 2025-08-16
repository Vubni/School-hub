from database.database import Database
from aiohttp import web
from functions import mail
from core import generate_unique_code
from config import bot

async def info(user_id:int):
    async with Database() as db:
        res = await db.execute("SELECT login, email, name, surname, class_number, class_letter, telegram_id FROM users WHERE id=$1", (user_id,))
    if res["telegram_id"]:
        try:
            res["telegram_name"] = (await bot.get_chat(res["telegram_id"])).username
        except:
            res["telegram_name"] = ""
    else:
        res["telegram_name"] = ""
    del res["telegram_id"]
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
        await mail.send_email_edit(email_new, token)
        await db.execute("INSERT INTO new_email (token, user_id, new_email) VALUES ($1, $2, $3)", (token, user_id, email_new))
    return web.Response(status=204)

async def set_password(user_id:int, password:str):
    async with Database() as db:
        res = await db.execute("SELECT 1 FROM users WHERE login = $1", (password,))
        if res:
            return web.json_response({"name": "login", "error": "The login has already been registered"}, status=409)
        await db.execute("UPDATE users SET login=$2 WHERE id=$1", (user_id, password))
    return web.Response(status=204)