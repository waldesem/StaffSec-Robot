import aiosqlite

from config import Config


async def get_item_id(table, column, name):
    async with aiosqlite.connect(Config.DATABASE_URI) as conn:
        async with conn.execute(
            f"SELECT * FROM {table} WHERE LOWER ({column}) = ?", (name.lower(),)
        ) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 1

def name_convert(fullname: str) -> str:
    return " ".join(filter(None, map(str.strip, fullname.split()))).upper()
