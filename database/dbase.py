from datetime import datetime

import sqlite3

from enums.classes import Categories, Regions, Statuses
from action.actions import get_item_id

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
                f"INSERT INTO persons (fullname, birthday, path, created, category_id, region_id, status_id) "
                f"VALUES (?, ?, ?, ?, ?, ?, ?)",
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
                "UPDATE persons SET path = ?, updated = ? WHERE id = ?",
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


def json_to_db(json_data):
    with sqlite3.connect(Config.DATABASE_URI) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM persons WHERE fullname = ? AND birthday = ?",
            (json_data["resume"]["fullname"], json_data["resume"]["birthday"]),
        )
        result = cursor.fetchone()
        person_id = result[0] if result else None

        if person_id:
            cursor.execute(
                f"UPDATE persons SET {'=?,'.join(json_data['resume'].keys())}=?, updated=? "
                f"WHERE id = {person_id}",
                tuple(json_data["resume"].values()) + (datetime.now(),),
            )
        else:
            cursor.execute(
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
                cursor.execute(
                    f"INSERT INTO {model} ({','.join(item.keys())}) "
                    f"VALUES ({','.join(['?'] * len(item.values()))})",
                    tuple(item.values()),
                )

        conn.commit()


def excel_to_db(excel):
    if excel.get("resume"):
        excel["resume"].update({
            "category_id": get_item_id("categories", "category", Categories.candidate.value),
            "status_id": get_item_id("statuses", "status", Statuses.finish.value),
            "region_id": get_item_id("regions", "region", Regions.MAIN_OFFICE.value),
            })

        with sqlite3.connect(Config.DATABASE_URI) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM persons WHERE fullname = ? AND birthday = ?",
                (excel["resume"]["fullname"], excel["resume"]["birthday"]),
            )
            result = cursor.fetchone()
            if result:
                person_id = result[0]
            else:
                person_id = None

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

            if excel.get("check"):
                cursor.execute(
                    f"INSERT INTO checks ({','.join(excel['check'].keys())},person_id) "
                    f"VALUES ({','.join(['?'] * len(excel['check'].values()))},?)",
                    tuple(excel["check"].values()) + (person_id,),
                )
            elif excel.get("robot"):
                cursor.execute(
                    f"INSERT INTO robots ({','.join(excel['robot'].keys())}, person_id) "
                    f"VALUES ({','.join(['?'] * len(excel['robot'].values()))}, ?)",
                    tuple(excel["robot"].values()) + (person_id,),
                )

            conn.commit()