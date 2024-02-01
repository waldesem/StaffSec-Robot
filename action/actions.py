import aiosqlite

from config import Config


async def get_category_id(name):
    async with aiosqlite.connect(Config.DATABASE_URI) as conn:
        async with conn.execute(
            "SELECT * FROM categories WHERE category = ?", (name,)
        ) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 1


async def get_status_id(name):
    async with aiosqlite.connect(Config.DATABASE_URI) as conn:
        async with conn.execute(
            "SELECT * FROM statuses WHERE status = ?", (name,)
        ) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 1


async def get_region_id(name):
    async with aiosqlite.connect(Config.DATABASE_URI) as conn:
        async with conn.execute(
            "SELECT id FROM regions WHERE region = ?", (name,)
        ) as cursor:
            return await cursor.fetchone()


async def get_conclusion_id(name):
    async with aiosqlite.connect(Config.DATABASE_URI) as conn:
        async with conn.execute(
            "SELECT * FROM conclusions WHERE LOWER (conclusion) = ?", (name.lower(),)
        ) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 1


def name_convert(fullname: str) -> str:
    return " ".join(filter(None, map(str.strip, fullname.split()))).upper()
