import aiosqlite

from config import Config


async def get_item_id(table, column, name):
    if not name:
        return 1
    async with aiosqlite.connect(Config.DATABASE_URI) as conn:
        async with conn.execute(
            f"SELECT * FROM {table} WHERE LOWER ({column}) LIKE LOWER (?)", (name,)
        ) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 1

def name_convert(fullname: str) -> str:
    return " ".join(filter(None, map(str.strip, fullname.split()))).upper()
