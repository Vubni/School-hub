from typing import List, Optional
from asyncpg import Record
from database.database import Database
from core import generate_unique_code
from aiohttp import web
import config

async def verify_email(email):
    async with Database() as db:
        await db.execute("UPDATE users SET verified=true WHERE email=$1", (email,))

async def register_user(email : str, password : str, first_name: str) -> str:
    """Регистрация нового пользователя в системе

    Args:
        first_name (str): _description_
        email (str): _description_
        password (str): _description_

    Returns:
        str: _description_
    """
    async with Database() as db:
        res = await db.execute("SELECT 1 FROM users WHERE email = $1", (email,))
        if res:
            return web.json_response({"name": "email", "error": "The email has already been registered"}, status=409)
        res = await db.execute("SELECT 1 FROM users WHERE first_name = $1", (first_name,))
        if res:
            return web.json_response({"name": "first_name", "error": "The first_name has already been registered"}, status=409)
        
        await db.execute(
            "INSERT INTO users (first_name, email, password) VALUES ($1, $2, $3)",
            (first_name, email, password)
        )
        await db.execute("DELETE FROM tokens WHERE date < CURRENT_DATE - INTERVAL '1 month'")
        code = generate_unique_code()
        await db.execute("INSERT INTO tokens (email, token) VALUES ($1, $2)", (email, code,))
    return code
            
async def auth(identifier:str, password:str) -> str:
    async with Database() as db:
        res = await db.execute("SELECT email FROM users WHERE (email = $1 or first_name = $1) AND password=$2", (identifier, password))
        if not res:
            return web.Response(status=401, text="The login information is incorrect")
        email = res["email"]
        await db.execute("DELETE FROM tokens WHERE date < CURRENT_DATE - INTERVAL '1 month'")
        code = generate_unique_code()
        await db.execute("INSERT INTO tokens (email, token) VALUES ($1, $2)", (email, code,))
    return web.json_response({"token": code}, status=200)


async def profile_get(email):
    async with Database() as db:
        res = await db.execute("SELECT email, first_name, verified FROM users WHERE email=$1", (email,))
    return res

async def profile_delete(email):
    async with Database() as db:
        res = await db.execute("SELECT * FROM users WHERE email=$1", (email,))
        if not res:
            return web.json_response({"error": "Profile not found"}, status=404)
        await db.execute("DELETE FROM users WHERE email=$1", (email,))
    return web.Response(status=204)

async def profile_edit(email:str, email_new:str, first_name:str, password_old:str, password_new:str):
    async with Database() as db:
        if email_new:
            res = await db.execute("SELECT 1 FROM users WHERE email = $1", (email_new,))
            if res:
                return web.json_response({"name": "email", "error": "The email has already been registered"}, status=409)
            await db.execute("UPDATE users SET email=$2 WHERE email=$1", (email, email_new))
            email = email_new
        if first_name:
            res = await db.execute("SELECT 1 FROM users WHERE first_name = $1", (first_name,))
            if res:
                return web.json_response({"name": "first_name", "error": "The first_name has already been registered"}, status=409)
            await db.execute("UPDATE users SET first_name=$2 WHERE email=$1", (email, first_name))
        if password_old and password_new:
            res = await db.execute("SELECT 1 FROM users WHERE email=$1 AND password=$2", (email, password_old))
            if not res:
                return web.json_response({"error": "Password is incorrect", "errors": [{"name": "password_old", "type": "incorrect", "message": "Password is incorrect", "value": password_old}]}, status=400)
            await db.execute("UPDATE users SET password=$3 WHERE email=$1 AND password=$2", (email, password_old, password_new))
    return web.Response(status=204)
