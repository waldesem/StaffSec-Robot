import os
import json
from datetime import date, datetime

import aiosqlite

from config import Config


async def json_to_db(json_path, json_file):
    json_data = await screen_json(os.path.join(json_path, json_file))

    async with aiosqlite.connect(Config.DATABASE_URI) as db:
        async with db.execute(
            "SELECT * FROM persons WHERE fullname = ? AND birthday = ?",
            (json_data["resume"]["fullname"], json_data["resume"]["birthday"]),
        ) as cursor:
            result = await cursor.fetchone()
            person_id = result[0] if result else None

            if person_id:
                await db.execute(
                    f"UPDATE persons SET {'=?,'.join(json_data['resume'].keys())}=? "
                    f"WHERE id = {person_id}",
                    tuple(json_data["resume"].values()),
                )
            else:
                await db.execute(
                    f"INSERT INTO persons ({','.join(json_data['resume'].keys())}) "
                    f"VALUES ({','.join(['?'] * len(json_data['resume'].values()))})",
                    tuple(json_data["resume"].values()),
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


async def screen_json(file):
    with open(file, "r", newline="", encoding="utf-8-sig") as f:
        json_dict = json.load(f)
        json_data = {}

        json_data.update(
            {
                "resume": {
                    "region_id": await parse_region(json_dict),
                    "category_id": await get_category_id("Кандидат"),
                    "status_id": await get_status_id("Окончено"),
                    "fullname": await parse_fullname(json_dict),
                    "previous": await parse_previous(json_dict),
                    "birthday": json_dict.get("birthday", date.today()),
                    "birthplace": json_dict.get("birthplace", ""),
                    "country": json_dict.get("citizen" ""),
                    "ext_country": json_dict.get("additionalCitizenship", ""),
                    "snils": json_dict.get("snils", ""),
                    "inn": json_dict.get("inn", ""),
                    "marital": json_dict.get("maritalStatus", ""),
                    "education": await parse_education(json_dict),
                }
            }
        )
        json_data.update(
            {
                "passport": [
                    {
                        "view": "Паспорт",
                        "series": json_dict.get("passportSerial", ""),
                        "number": json_dict.get("passportNumber", ""),
                        "issue": datetime.strptime(
                            json_dict.get("passportIssueDate", "1900-01-01"), "%Y-%m-%d"
                        ),
                        "agency": json_dict.get("passportIssuedBy", ""),
                    }
                ]
            }
        )
        json_data.update(
            {
                "addresses": [
                    {
                        "view": "Адрес регистрации",
                        "address": json_dict.get("regAddress", ""),
                    },
                    {
                        "view": "Адрес проживания",
                        "address": json_dict.get("validAddress", ""),
                    },
                ]
            }
        )
        json_data.update(
            {
                "contacts": [
                    {
                        "view": "Мобильный телефон",
                        "contact": json_dict.get("contactPhone", ""),
                    },
                    {
                        "view": "Электронная почта",
                        "contact": json_dict.get("email", ""),
                    },
                ]
            }
        )
        json_data.update(
            {
                "staff": [
                    {
                        "position": json_dict.get("positionName", ""),
                        "department": json_dict.get("department", ""),
                    }
                ]
            }
        )
        json_data.update({"workplaces": await parse_workplace(json_dict)})
        json_data.update({"affilation": await parse_affilation(json_dict)})

        return json_data


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


async def parse_region(json_dict):
    if "department" in json_dict:
        region_id = 1
        divisions = json_dict["department"].split("/")
        for div in divisions:
            region = await get_region_id(div)
            if region:
                region_id = region[0]
        return region_id


async def parse_fullname(json_dict):
    lastName = json_dict.get("lastName", "None").strip()
    firstName = json_dict.get("firstName", "None").strip()
    midName = json_dict.get("midName", "").strip()
    return f"{lastName} {firstName} {midName}".upper().rstrip()


async def parse_previous(json_dict):
    if "hasNameChanged" in json_dict:
        if len(json_dict["nameWasChanged"]):
            previous = []
            for item in json_dict["nameWasChanged"]:
                firstNameBeforeChange = item.get("firstNameBeforeChange", "")
                lastNameBeforeChange = item.get("lastNameBeforeChange", "")
                midNameBeforeChange = item.get("midNameBeforeChange", "")
                yearOfChange = str(item.get("yearOfChange", ""))
                reason = str(item.get("reason", ""))
                previous.append(
                    f"{yearOfChange} - {firstNameBeforeChange} "
                    f"{lastNameBeforeChange} {midNameBeforeChange}, "
                    f"{reason}".replace("  ", "")
                )
            return "; ".join(previous)
    return ""


async def parse_education(json_dict):
    if "education" in json_dict:
        if len(json_dict["education"]):
            education = []
            for item in json_dict["education"]:
                institutionName = item.get("institutionName")
                endYear = item.get("endYear", "н.в.")
                specialty = item.get("specialty")
                education.append(
                    f"{str(endYear)} - {institutionName}, "
                    f"{specialty}".replace("  ", "")
                )
            return "; ".join(education)
    return ""


async def parse_workplace(json_dict):
    if "experience" in json_dict:
        if len(json_dict["experience"]):
            experience = []
            for item in json_dict["experience"]:
                work = {
                    "start_date": datetime.strptime(
                        item.get("beginDate", "1900-01-01"), "%Y-%m-%d"
                    ),
                    "end_date": datetime.strptime(item["endDate"], "%Y-%m-%d")
                    if "endDate" in item
                    else datetime.now(),
                    "workplace": item.get("name", ""),
                    "address": item.get("address", ""),
                    "position": item.get("position", ""),
                    "reason": item.get("fireReason", ""),
                }
                experience.append(work)
            return experience
    return []


async def parse_affilation(json_dict):
    affilation = []
    if json_dict["hasPublicOfficeOrganizations"]:
        if len(json_dict["publicOfficeOrganizations"]):
            for item in json_dict["publicOfficeOrganizations"]:
                public = {
                    "view": "Являлся государственным или муниципальным служащим",
                    "name": f"{item.get('name', '')}",
                    "position": f"{item.get('position', '')}",
                }
                affilation.append(public)

    if json_dict["hasStateOrganizations"]:
        if len(json_dict["stateOrganizations"]):
            for item in json_dict["publicOfficeOrganizations"]:
                state = {
                    "view": "Являлся государственным должностным лицом",
                    "name": f"{item.get('name', '')}",
                    "position": f"{item.get('position', '')}",
                }
                affilation.append(state)

    if json_dict["hasRelatedPersonsOrganizations"]:
        if len(json_dict["relatedPersonsOrganizations"]):
            for item in json_dict["relatedPersonsOrganizations"]:
                related = {
                    "view": "Связанные лица работают в госудраственных организациях",
                    "name": f"{item.get('name', '')}",
                    "position": f"{item.get('position', '')}",
                    "inn": f"{item.get('inn'), ''}",
                }
                affilation.append(related)

    if json_dict["hasOrganizations"]:
        if len(json_dict["organizations"]):
            for item in json_dict["organizations"]:
                organization = {
                    "view": 'Участвует в деятельности коммерческих организаций"',
                    "name": f"{item.get('name', '')}",
                    "position": f"{item.get('workCombinationTime', '')}",
                    "inn": f"{item.get('inn'), ''}",
                }
                affilation.append(organization)
    return affilation
