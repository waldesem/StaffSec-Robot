import os
import json
from datetime import datetime

from enums.classes import Categories, Statuses
from database.dbase import json_to_db
from action.actions import name_convert, get_item_id


async def screen_json(json_path, json_file):
    file = os.path.join(json_path, json_file)
    with open(file, "r", newline="", encoding="utf-8-sig") as f:
        json_dict = json.load(f)
        json_data = {}

        json_data.update(
            {
                "resume": {
                    "region_id": await parse_region(json_dict),
                    "category_id": await get_item_id(
                        "categories", "category", Categories.candidate.value
                    ),
                    "status_id": await get_item_id(
                        "statuses", "status", Statuses.finish.value
                    ),
                    "fullname": await parse_fullname(json_dict),
                    "previous": await parse_previous(json_dict),
                    "birthday": json_dict.get("birthday"),
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

        if all(
            [
                json_data["resume"]["fullname"] is not None,
                json_data["resume"]["birthday"] is not None,
            ]
        ):
            await json_to_db(json_data)


async def parse_region(json_dict):
    region_id = 1
    if json_dict.get("department") is not None:
        divisions = json_dict.get("department").split("/")
        for div in divisions:
            region = await get_item_id("regions", "region", div)
            if region:
                region_id = region
    return region_id


async def parse_fullname(json_dict):
    lastName = json_dict.get("lastName")
    firstName = json_dict.get("firstName")
    midName = json_dict.get("midName", "")
    if any([lastName is None, firstName is None]):
        return None
    return name_convert(f"{lastName} {firstName} {midName}")


async def parse_previous(json_dict):
    if json_dict.get("hasNameChanged"):
        if len(json_dict.get("nameWasChanged")):
            previous = []
            for item in json_dict.get("nameWasChanged"):
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
    if json_dict.get("education"):
        if len(json_dict.get("education")):
            education = []
            for item in json_dict.get("education"):
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
    if json_dict.get("experience"):
        if len(json_dict.get("experience")):
            experience = []
            for item in json_dict.get("experience"):
                work = {
                    "start_date": datetime.strptime(
                        item.get("beginDate", "1900-01-01"), "%Y-%m-%d"
                    ),
                    "end_date": (
                        datetime.strptime(item["endDate"], "%Y-%m-%d")
                        if "endDate" in item
                        else datetime.now()
                    ),
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
    if json_dict.get("hasPublicOfficeOrganizations"):
        if len(json_dict.get("publicOfficeOrganizations")):
            for item in json_dict.get("publicOfficeOrganizations"):
                public = {
                    "view": "Являлся государственным или муниципальным служащим",
                    "name": f"{item.get('name', '')}",
                    "position": f"{item.get('position', '')}",
                }
                affilation.append(public)

    if json_dict.get("hasStateOrganizations"):
        if len(json_dict.get("stateOrganizations")):
            for item in json_dict.get("publicOfficeOrganizations"):
                state = {
                    "view": "Являлся государственным должностным лицом",
                    "name": f"{item.get('name', '')}",
                    "position": f"{item.get('position', '')}",
                }
                affilation.append(state)

    if json_dict.get("hasRelatedPersonsOrganizations"):
        if len(json_dict.get("relatedPersonsOrganizations")):
            for item in json_dict.get("relatedPersonsOrganizations"):
                related = {
                    "view": "Связанные лица работают в госудраственных организациях",
                    "name": f"{item.get('name', '')}",
                    "position": f"{item.get('position', '')}",
                    "inn": f"{item.get('inn'), ''}",
                }
                affilation.append(related)

    if json_dict.get("hasOrganizations"):
        if len(json_dict.get("organizations")):
            for item in json_dict.get("organizations"):
                organization = {
                    "view": 'Участвует в деятельности коммерческих организаций"',
                    "name": f"{item.get('name', '')}",
                    "position": f"{item.get('workCombinationTime', '')}",
                    "inn": f"{item.get('inn'), ''}",
                }
                affilation.append(organization)
    return affilation
