from database.database import Database
from core import generate_unique_code
from aiohttp import web
import config

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
        res = await db.execute("SELECT email FROM users WHERE (email = $1 or login = $1) AND password=$2", (identifier, password))
        if not res:
            return web.Response(status=401, text="The login information is incorrect")
        email = res["email"]
        code = generate_unique_code()
        await db.execute("INSERT INTO tokens (email, token) VALUES ($1, $2)", (email, code,))
    return web.json_response({"token": code}, status=200)