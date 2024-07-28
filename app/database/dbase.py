from datetime import datetime
import sqlite3

from action.actions import get_item_id
from enums.classes import Categories, Regions, Statuses

from config import Config


def db_main_data(fullname, birthday, url):
    with sqlite3.connect(Config.DATABASE_URI) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM persons WHERE fullname = ? AND birthday = ?",
            (fullname, birthday),
        )
        result = cursor.fetchone()
        if not result:
            cursor.execute(
                "INSERT INTO persons (fullname, birthday, path, created, category_id, region_id, status_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    fullname,
                    birthday,
                    url,
                    datetime.now(),
                    get_item_id("categories", "category", Categories.candidate.value),
                    get_item_id("regions", "region", Regions.MAIN_OFFICE.value),
                    get_item_id("statuses", "status", Statuses.finish.value),
                ),
            )
        else:
            cursor.execute(
                "UPDATE persons SET path=?, updated=? WHERE id=?",
                (url, datetime.now(), result[0]),
            )
        conn.commit()


def db_iquiry_data(info, initiator, fullname, birthday):
    with sqlite3.connect(Config.DATABASE_URI) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM persons WHERE fullname = ? AND birthday = ?",
            (fullname, birthday),
        )
        result = cursor.fetchone()

        if not result:
            cursor.execute(
                "INSERT INTO persons (fullname, birthday, created, category_id, region_id, status_id) \
                            VALUES (?, ?, ?, ?, ?, ?)",
                (
                    fullname,
                    birthday,
                    datetime.now(),
                    get_item_id("categories", "category", Categories.staff.value),
                    get_item_id("regions", "region", Regions.MAIN_OFFICE.value),
                    get_item_id("statuses", "status", Statuses.finish.value),
                ),
            )
            result = [cursor.lastrowid]

        cursor.execute(
            "INSERT INTO inquiries (info, initiator, deadline, person_id) \
                        VALUES (?, ?, ?, ?)",
            (info, initiator, datetime.now(), result[0]),
        )
        conn.commit()


def json_to_db(json_data: dict):
    with sqlite3.connect(Config.DATABASE_URI) as conn:
        cursor = conn.cursor()
        for key, items in json_data.items():
            if key == "resume":
                cursor.execute(
                    "SELECT * FROM persons WHERE fullname = ? AND birthday = ?",
                    (items["fullname"], items["birthday"]),
                )
                result = cursor.fetchone()
                person_id = result[0] if result else None

                if person_id:
                    cursor.execute(
                        f"UPDATE persons SET {'=?,'.join(items.keys())}=?, updated=? "
                        f"WHERE id = {person_id}",
                        tuple(items.values()) + (datetime.now(),),
                    )
                else:
                    cursor.execute(
                        f"INSERT INTO persons ({','.join(items.keys())},created) "
                        f"VALUES ({','.join(['?'] * len(items.values()))},?)",
                        tuple(items.values()) + (datetime.now(),),
                    )
                    person_id = cursor.lastrowid

            else:
                for item in items:
                    item["person_id"] = person_id
                    cursor.execute(
                        f"INSERT INTO {key} ({','.join(item.keys())}) "
                        f"VALUES ({','.join(['?'] * len(item.values()))})",
                        tuple(item.values()),
                    )
        conn.commit()
        

def excel_to_db(excel):
    if "resume" in excel:
        excel["resume"]["category_id"] = get_item_id(
            "categories", "category", Categories.candidate.value
        )
        excel["resume"]["status_id"] = get_item_id(
            "statuses", "status", Statuses.finish.value
        )
        excel["resume"]["region_id"] = get_item_id(
            "regions", "region", Regions.MAIN_OFFICE.value
        )

        with sqlite3.connect(Config.DATABASE_URI) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM persons WHERE fullname = ? AND birthday = ?",
                (excel["resume"]["fullname"], excel["resume"]["birthday"]),
            )
            result = cursor.fetchone()
            person_id = result[0] if result else None

            if not person_id:
                cursor = cursor.execute(
                    f"INSERT INTO persons ({','.join(excel['resume'].keys())},created) "
                    f"VALUES ({','.join(['?'] * len(excel['resume'].values()))},?)",
                    tuple(excel["resume"].values()) + (datetime.now(),),
                )
                person_id = cursor.lastrowid
            else:
                cursor.execute(
                    f"UPDATE persons SET {'=?,'.join(excel['resume'].keys())}=?, updated=? "
                    f"WHERE id = {person_id}",
                    tuple(excel["resume"].values()) + (datetime.now(),),
                )
            if "check" in excel:
                cursor.execute(
                    f"INSERT INTO checks ({','.join(excel['check'].keys())},person_id) "
                    f"VALUES ({','.join(['?'] * len(excel['check'].values()))},?)",
                    tuple(excel["check"].values()) + (person_id,),
                )
            conn.commit()
