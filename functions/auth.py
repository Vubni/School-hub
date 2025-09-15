from database.database import Database
from core import generate_unique_code
from aiohttp import web
import config
from functions import mail

async def verify_email(email):
    async with Database() as db:
        await db.execute("UPDATE users SET verified=true WHERE email=$1", (email,))

# async def register_user(email : str, password : str, first_name: str) -> str:
#     """Регистрация нового пользователя в системе

#     Args:
#         first_name (str): _description_
#         email (str): _description_
#         password (str): _description_

#     Returns:
#         str: _description_
#     """
#     async with Database() as db:
#         res = await db.execute("SELECT 1 FROM users WHERE email = $1", (email,))
#         if res:
#             return web.json_response({"name": "email", "error": "The email has already been registered"}, status=409)
#         res = await db.execute("SELECT 1 FROM users WHERE first_name = $1", (first_name,))
#         if res:
#             return web.json_response({"name": "first_name", "error": "The first_name has already been registered"}, status=409)
        
#         await db.execute(
#             "INSERT INTO users (first_name, email, password) VALUES ($1, $2, $3)",
#             (first_name, email, password)
#         )
#         code = generate_unique_code()
#         await db.execute("INSERT INTO tokens (email, token) VALUES ($1, $2)", (email, code,))
#     return code
            
async def auth(identifier:str, password:str) -> str:
    async with Database() as db:
        res = await db.execute("SELECT id FROM users WHERE (email = $1 or login = $1) AND password=$2", (identifier, password))
        if not res:
            return web.Response(status=401, text="The login information is incorrect")
        user_id = res["id"]
        code = generate_unique_code()
        await db.execute("INSERT INTO tokens (user_id, token) VALUES ($1, $2)", (user_id, code,))
    return web.json_response({"token": code}, status=200)

async def check_auth_token(token:str):
    async with Database() as db:
        res = await db.execute("SELECT user_id FROM auth_tokens WHERE token = $1", (token,))
        if not res:
            return web.Response(status=401)
        await db.execute("INSERT INTO tokens (user_id, token) VALUES ($1, $2)", (res["user_id"], token,))
    return web.json_response({"token": token}, status=200)

async def forgot_password(identifier: str, new_password: str) -> web.Response:
    async with Database() as db:
        res = await db.execute("SELECT id, email, telegram_id FROM users WHERE (email = $1 or login = $1)", (identifier,))
        if not res:
            return web.Response(status=401, text="The login information is incorrect")
        if not res["email"] and not res["telegram_id"]:
            return web.Response(status=422, text="Email and Telegram account are not linked to the user")
        result = await db.fetchval("INSERT INTO new_password_wait (user_id, new_password) VALUES ($1, $2)", (res["id"], new_password,))
        if res["telegram_id"]:
            await config.bot.send_message(res["telegram_id"], f"Вы запросили смену пароля. Если это были не вы, просто <b>проигнорируйте</b> это сообщение.\n\nЕсли это были вы, перейдите по ссылке ниже, чтобы подтвердить смену пароля:\nhttps://api.school-hub.ru/auth/forgot_password/confirm?confirm={result}")
        if res["email"]:
            await mail.send_password_edit(res["email"], f"https://api.school-hub.ru/auth/forgot_password/confirm?confirm={result}")
        return web.Response(status=204)
    
async def forgot_password_confirm(confirm: int) -> web.Response:
    async with Database() as db:
        res = await db.execute("SELECT user_id, new_password FROM new_password_wait WHERE id = $1", (confirm,))
        if not res:
            return web.Response(status=400, text="Invalid confirmation code")
        await db.execute("UPDATE users SET password=$1 WHERE id=$2", (res["new_password"], res["user_id"],))
        await db.execute("DELETE FROM new_password_wait WHERE id=$1", (confirm,))
        return web.HTTPFound('/forgot_password/')
    
async def email_verify_confirm(token: str) -> web.Response:
    async with Database() as db:
        res = await db.execute("SELECT user_id, new_email FROM new_email WHERE token = $1", (token,))
        if not res:
            return web.Response(status=400, text="Invalid confirmation code")
        await db.execute("UPDATE users SET email=$1 WHERE id=$2", (res["new_email"], res["user_id"],))
        await db.execute("DELETE FROM new_email WHERE token=$1", (token,))
        return web.HTTPFound('/new_email/')