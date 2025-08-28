from database.database import Database
from aiohttp import web

async def check_token(token):
    async with Database() as db:
        res = await db.execute("SELECT user_id FROM tokens WHERE token=$1", (token,))
        if not res:
            return web.Response(status=401, text="Invalid token")
    return int(res["user_id"])

async def init_db():
    async with Database() as db:
        try:
            # Сначала создаем таблицы без внешних ключей
            await db.execute("""
                CREATE TABLE IF NOT EXISTS public.users
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    email character varying COLLATE pg_catalog."default",
    name character varying COLLATE pg_catalog."default" NOT NULL,
    surname character varying COLLATE pg_catalog."default" NOT NULL,
    password character varying COLLATE pg_catalog."default" NOT NULL,
    telegram_id bigint,
    login character varying(20) COLLATE pg_catalog."default" NOT NULL,
    class_number integer NOT NULL,
    class_letter character varying(1) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT users_pkey PRIMARY KEY (id),
    CONSTRAINT users_email_key UNIQUE (email)
)""")
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS public.subjects
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 999999999999999999 CACHE 1 ),
    title character varying(20) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT subjects_pkey PRIMARY KEY (id)
)""")
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS public.administrations
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 999999999999999999 CACHE 1 ),
    title character varying(64) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT administrations_pkey PRIMARY KEY (id)
)""")
            
            # Затем таблицы, которые ссылаются на ранее созданные
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
                CREATE TABLE IF NOT EXISTS public.teachers
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 999999999999999 CACHE 1 ),
    name character varying(60) COLLATE pg_catalog."default" NOT NULL,
    admin boolean NOT NULL DEFAULT false,
    subject bigint NOT NULL,
    CONSTRAINT teachers_pkey PRIMARY KEY (id),
    CONSTRAINT subject FOREIGN KEY (subject)
        REFERENCES public.subjects (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)""")
            
            # Остальные таблицы в правильном порядке зависимостей
            await db.execute("""
                CREATE TABLE IF NOT EXISTS public.olympiads
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 999999999999999999 CACHE 1 ),
    title character varying(120) COLLATE pg_catalog."default" NOT NULL,
    description character varying(360) COLLATE pg_catalog."default" NOT NULL,
    image_path character varying(256) COLLATE pg_catalog."default" NOT NULL,
    date date NOT NULL DEFAULT CURRENT_DATE,
    url character varying(512) COLLATE pg_catalog."default",
    CONSTRAINT olympiads_pkey PRIMARY KEY (id)
)""")
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS public.offices
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 999999999999999999 CACHE 1 ),
    office character varying(16) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT offices_pkey PRIMARY KEY (id)
)""")
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS public.news_achievements
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 999999999999999999 CACHE 1 ),
    title character varying(120) COLLATE pg_catalog."default" NOT NULL,
    description character varying(360) COLLATE pg_catalog."default" NOT NULL,
    image_path character varying(256) COLLATE pg_catalog."default" NOT NULL,
    date date NOT NULL DEFAULT CURRENT_DATE,
    url character varying(512) COLLATE pg_catalog."default",
    CONSTRAINT news_achievements_pkey PRIMARY KEY (id)
)""")
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS public.new_email
(
    token character varying(32) COLLATE pg_catalog."default" NOT NULL,
    user_id bigint NOT NULL,
    new_email character varying(256) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT user_id FOREIGN KEY (user_id)
        REFERENCES public.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
)""")
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS public.lessons
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 999999999999999999 CACHE 1 ),
    title character varying(20) COLLATE pg_catalog."default" NOT NULL,
    day_number integer NOT NULL,
    lesson_number integer NOT NULL,
    classrooms integer[],
    teachers character varying(32)[] COLLATE pg_catalog."default",
    class_number integer NOT NULL,
    class_letter character varying(1) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT schedule_pkey PRIMARY KEY (id)
)""")
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS public.lesson_time
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 999999999999999999 CACHE 1 ),
    day_number integer NOT NULL,
    start_time character varying(5) COLLATE pg_catalog."default" NOT NULL,
    stop_time character varying(5) COLLATE pg_catalog."default" NOT NULL,
    lesson_number integer NOT NULL,
    CONSTRAINT lesson_time_pkey PRIMARY KEY (id)
)""")
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS public.lesson_time_special
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 999999999999999999 CACHE 1 ),
    date date NOT NULL,
    lesson_number integer NOT NULL,
    start_time character varying(5) COLLATE pg_catalog."default" NOT NULL,
    stop_time character varying(5) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT lesson_time_special_pkey PRIMARY KEY (id)
)""")
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS public.lesson_substitutions
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 999999999999999999 CACHE 1 ),
    date date NOT NULL,
    title character varying(20) COLLATE pg_catalog."default" NOT NULL,
    lesson_number integer NOT NULL,
    classrooms integer[],
    teachers character varying[] COLLATE pg_catalog."default",
    class_number integer NOT NULL,
    class_letter character varying(1) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT lesson_substitutions_pkey PRIMARY KEY (id)
)""")
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS public.events
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 999999999999999999 CACHE 1 ),
    title character varying(120) COLLATE pg_catalog."default" NOT NULL,
    description character varying(360) COLLATE pg_catalog."default" NOT NULL,
    image_path character varying(256) COLLATE pg_catalog."default" NOT NULL,
    date date NOT NULL DEFAULT CURRENT_DATE,
    url character varying(512) COLLATE pg_catalog."default",
    CONSTRAINT events_pkey PRIMARY KEY (id)
)""")
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS public.clubs
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 99999999999999 CACHE 1 ),
    title character varying(32) COLLATE pg_catalog."default" NOT NULL,
    description character varying(200) COLLATE pg_catalog."default" NOT NULL,
    image_path character varying(100) COLLATE pg_catalog."default",
    telegram_url character varying(120) COLLATE pg_catalog."default" DEFAULT NULL::character varying,
    administration integer NOT NULL,
    xp integer NOT NULL DEFAULT 0,
    max_members_counts integer DEFAULT 0,
    class_limit_min integer DEFAULT 1,
    class_limit_max integer DEFAULT 11,
    CONSTRAINT clubs_pkey PRIMARY KEY (id),
    CONSTRAINT title UNIQUE (title),
    CONSTRAINT administration FOREIGN KEY (administration)
        REFERENCES public.administrations (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)""")
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS public.club_members
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9999999999999 CACHE 1 ),
    user_id bigint NOT NULL,
    club_id bigint NOT NULL,
    admin boolean NOT NULL DEFAULT false,
    CONSTRAINT club_members_pkey PRIMARY KEY (id),
    CONSTRAINT club_id FOREIGN KEY (club_id)
        REFERENCES public.clubs (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT user_id FOREIGN KEY (user_id)
        REFERENCES public.users (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
)""")
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS public.auth_tokens
(
    token character varying(32) COLLATE pg_catalog."default" NOT NULL,
    user_id bigint NOT NULL,
    CONSTRAINT auth_tokens_pkey PRIMARY KEY (token),
    CONSTRAINT auth_tokens_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES public.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
)""")
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS public.achievements
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9999999999999999 CACHE 1 ),
    global boolean NOT NULL DEFAULT true,
    title character varying(20) COLLATE pg_catalog."default" NOT NULL,
    description character varying(120) COLLATE pg_catalog."default" NOT NULL,
    xp integer NOT NULL DEFAULT 0,
    CONSTRAINT achievements_pkey PRIMARY KEY (id)
)""")
        except Exception as e:
            print(f"Ошибка при создании таблицы: {e}")