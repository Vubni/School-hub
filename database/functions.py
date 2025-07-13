from database.database import Database
from aiohttp import web

async def check_token(token):
    async with Database() as db:
        await db.execute("DELETE FROM tokens WHERE date < CURRENT_DATE - INTERVAL '1 month'")
        res = await db.execute("SELECT email FROM tokens WHERE token=$1", (token,))
        if not res:
            return web.Response(status=401, text="Invalid token")
    return res["email"]

async def init_db():
    async with Database() as db:
        try:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id BIGINT NOT NULL GENERATED ALWAYS AS IDENTITY (
                        INCREMENT 1 START 1 MINVALUE 1 CACHE 1
                    ),
                    email VARCHAR UNIQUE NOT NULL,
                    first_name VARCHAR UNIQUE NOT NULL,
                    password VARCHAR NOT NULL,
                    verified BOOLEAN DEFAULT FALSE,
                    PRIMARY KEY (id)
                );

                -- Индексы для поиска по email и first_name
                CREATE UNIQUE INDEX idx_users_email ON users(email);
                CREATE UNIQUE INDEX idx_users_first_name ON users(first_name);""")
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS tokens (
                    token VARCHAR PRIMARY KEY,
                    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    date DATE DEFAULT CURRENT_DATE
                );

                -- Индексы для оптимизации поиска
                CREATE INDEX idx_tokens_user_id ON tokens(user_id);
                CREATE INDEX idx_tokens_date ON tokens(date);""")
        except Exception as e:
            print(f"Ошибка при создании таблицы: {e}")