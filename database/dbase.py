from datetime import datetime

import aiosqlite

from enums.classes import Categories, Regions, Statuses
from action.actions import get_item_id

from config import Config


"""
db_main_data asynchronously inserts or updates a person record in the database.

Parameters:
- fullname (str): The person's full name.  
- birthday (datetime): The person's date of birth.
- url (str): The url/path to the person's profile.

It first checks if a record already exists for the given fullname and birthday. 
If not, it inserts a new record. If so, it updates the existing record's path and 
updated fields.
"""
async def db_main_data(fullname, birthday, url):
    async with aiosqlite.connect(Config.DATABASE_URI) as db:
        async with db.execute(
            "SELECT * FROM persons WHERE fullname = ? AND birthday = ?",
            (fullname, birthday),
        ) as cursor:
            result = await cursor.fetchone()
            if not result:
                await db.execute(
                    f"INSERT INTO persons (fullname, birthday, path, created, category_id, region_id, status_id) "
                    f"VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        fullname,
                        birthday,
                        url,
                        datetime.now(),
                        await get_item_id("categories", "category", Categories.candidate.value),
                        await get_item_id("regions", "region", Regions.MAIN_OFFICE.value),
                        await get_item_id("statuses", "status", Statuses.finish.value),
                    ),
                )

            else:
                await db.execute(
                    "UPDATE persons SET path = ?, updated = ? WHERE id = ?",
                    (url, datetime.now(), result[0]),
                )

            await db.commit()


"""
db_iquiry_data asynchronously inserts a person record and inquiry record in the database.

It first checks if a record already exists for the given fullname and birthday.
If not, it inserts a new person record. 

It then inserts a new inquiry record, linking it to the person record.

Parameters:
- info (str): Details about the inquiry.
- initiator (str): Name of person initiating inquiry.  
- fullname (str): The person's full name.
- birthday (datetime): The person's date of birth.
"""
async def db_iquiry_data(info, initiator, fullname, birthday):
    async with aiosqlite.connect(Config.DATABASE_URI) as db:
        async with db.execute(
            "SELECT * FROM persons WHERE fullname = ? AND birthday = ?",
            (fullname, birthday),
        ) as cursor:
            result = await cursor.fetchone()

            if not result:
                await db.execute(
                    "INSERT INTO persons (fullname, birthday, created, category_id, region_id, status_id) \
                                VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        fullname, 
                        birthday, 
                        datetime.now(), 
                        await get_item_id("categories", "category", Categories.staff.value),
                        await get_item_id("regions", "region", Regions.MAIN_OFFICE.value),
                        await get_item_id("statuses", "status", Statuses.finish.value),
                    ),
                )
                result = [cursor.lastrowid]

            await db.execute(
                "INSERT INTO inquiries (info, initiator, deadline, person_id) \
                            VALUES (?, ?, ?, ?)",
                (info, initiator, datetime.now(), result[0]),
            )

            await db.commit()



"""
json_to_db asynchronously inserts person data from JSON into the database.

It first checks if a person record already exists matching the fullname and birthday. 
If so, it updates that existing record.
Otherwise, it inserts a new person record.

It then inserts related records in other tables like staff, documents, etc. 
linking them to the person record.

Parameters:
- json_data (dict): The JSON data to insert into the database.
"""
async def json_to_db(json_data):
    async with aiosqlite.connect(Config.DATABASE_URI) as db:
        async with db.execute(
            "SELECT * FROM persons WHERE fullname = ? AND birthday = ?",
            (json_data["resume"]["fullname"], json_data["resume"]["birthday"]),
        ) as cursor:
            result = await cursor.fetchone()
            person_id = result[0] if result else None

            if person_id:
                await db.execute(
                    f"UPDATE persons SET {'=?,'.join(json_data['resume'].keys())}=?, updated=? "
                    f"WHERE id = {person_id}",
                    tuple(json_data["resume"].values()) + (datetime.now(),),
                )
            else:
                await db.execute(
                    f"INSERT INTO persons ({','.join(json_data['resume'].keys())},created) "
                    f"VALUES ({','.join(['?'] * len(json_data['resume'].values()))},?)",
                    tuple(json_data["resume"].values()) + (datetime.now(),),
                )
                person_id = cursor.lastrowid

            models = [
                "staffs",
                "documents",
                "addresses",
                "contacts",
                "workplaces",
                "affilations",
            ]
            items_lists = [
                json_data["staff"],
                json_data["passport"],
                json_data["addresses"],
                json_data["contacts"],
                json_data["workplaces"],
                json_data["affilation"],
            ]

            for model, items_list in zip(models, items_lists):
                for item in items_list:
                    item["person_id"] = person_id
                    await db.execute(
                        f"INSERT INTO {model} ({','.join(item.keys())}) "
                        f"VALUES ({','.join(['?'] * len(item.values()))})",
                        tuple(item.values()),
                    )

        await db.commit()


"""Updates a database with data from an Excel file.

Iterates through the Excel data, checking if a person record exists. If not, creates a new person record. 
Updates the person record with the latest data. Also inserts related check and robot data referencing the person ID.

Commits changes after inserting/updating each record.
"""
async def excel_to_db(excel):
    if excel.get("resume"):
        excel["resume"].update({
            "category_id": await get_item_id("categories", "category", Categories.candidate.value),
            "status_id": await get_item_id("statuses", "status", Statuses.finish.value),
            "region_id": await get_item_id("regions", "region", Regions.MAIN_OFFICE.value),
            })

        async with aiosqlite.connect(Config.DATABASE_URI) as db:
            async with db.execute(
                "SELECT * FROM persons WHERE fullname = ? AND birthday = ?",
                (excel["resume"]["fullname"], excel["resume"]["birthday"]),
            ) as cursor:
                result = await cursor.fetchone()
                if result:
                    person_id = result[0]
                else:
                    person_id = None

            if not person_id:
                cursor = await db.execute(
                    f"INSERT INTO persons ({','.join(excel['resume'].keys())},created) "
                    f"VALUES ({','.join(['?'] * len(excel['resume'].values()))},?)",
                    tuple(excel["resume"].values()) + (datetime.now(),),
                )
                await db.commit()
                person_id = cursor.lastrowid
            else:
                await db.execute(
                    f"UPDATE persons SET {'=?,'.join(excel['resume'].keys())}=?, updated=? "
                    f"WHERE id = {person_id}",
                    tuple(excel["resume"].values()) + (datetime.now(),),
                )

            if excel.get("check"):
                await db.execute(
                    f"INSERT INTO checks ({','.join(excel['check'].keys())},person_id) "
                    f"VALUES ({','.join(['?'] * len(excel['check'].values()))},?)",
                    tuple(excel["check"].values()) + (person_id,),
                )
            elif excel.get("robot"):
                await db.execute(
                    f"INSERT INTO robots ({','.join(excel['robot'].keys())}, person_id) "
                    f"VALUES ({','.join(['?'] * len(excel['robot'].values()))}, ?)",
                    tuple(excel["robot"].values()) + (person_id,),
                )

            await db.commit()
