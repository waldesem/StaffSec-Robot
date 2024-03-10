import sqlite3  

from config import Config


"""Gets the ID for the given name from the specified table and column.

Args:
  table: The name of the table to query.
  column: The name of the column to search.
  name: The name to search for.

Returns: 
  The ID for the given name if found, otherwise 1.
"""
def get_item_id(table, column, name):
    if not name:
        return 1
    
    with sqlite3.connect(Config.DATABASE_URI) as conn:
        cursor = conn.cursor()
        cursor.execute(
          f"SELECT * FROM {table} WHERE LOWER ({column}) LIKE LOWER (?)", (name,)
        )
        result = cursor.fetchone()
        return result[0] if result else 1

"""Converts a full name to uppercase with spaces between words.

Strips leading and trailing whitespace from each part of the name, and
filters out empty strings. Joins the parts with spaces and converts to 
uppercase.

Args:
  fullname: The full name to convert.

Returns:
  The converted uppercase name with spaces.
"""
def name_convert(fullname: str) -> str:
    return " ".join(filter(None, map(str.strip, fullname.split()))).upper()
