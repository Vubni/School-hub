from database.database import Database
from aiohttp import web

async def check_token(token):
    async with Database() as db:
        res = await db.execute("SELECT user_id FROM tokens WHERE token=$1", (token,))
        if not res:
            return web.Response(status=401, text="Invalid token")
    return res["email"]

async def init_db():
    async with Database() as db:
        try:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS public.users
                (
                    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
                    email character varying COLLATE pg_catalog."default",
                    name character varying COLLATE pg_catalog."default" NOT NULL,
                    surname character varying COLLATE pg_catalog."default" NOT NULL,
                    password character varying COLLATE pg_catalog."default" NOT NULL,
                    telegram_id bigint NOT NULL,
                    CONSTRAINT users_pkey PRIMARY KEY (id),
                    CONSTRAINT users_email_key UNIQUE (email)
                )""")
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS public.tokens
                (
                    token character varying(32) COLLATE pg_catalog."default" NOT NULL,
                    user_id bigint NOT NULL,
                    CONSTRAINT tokens_pkey PRIMARY KEY (token),
                    CONSTRAINT tokens_user_id_fkey FOREIGN KEY (user_id)
                        REFERENCES public.users (id) MATCH SIMPLE
                        ON UPDATE NO ACTION
                        ON DELETE CASCADE
                )""")
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS public.new_email
                (
                    token character varying(128) COLLATE pg_catalog."default" NOT NULL,
                    user_id bigint NOT NULL,
                    new_email character varying(256) COLLATE pg_catalog."default" NOT NULL,
                    CONSTRAINT user_id FOREIGN KEY (user_id)
                        REFERENCES public.users (id) MATCH SIMPLE
                        ON UPDATE NO ACTION
                        ON DELETE CASCADE
                )""")
        except Exception as e:
            print(f"Ошибка при создании таблицы: {e}")