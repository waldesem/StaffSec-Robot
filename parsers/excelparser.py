import os
from datetime import date, datetime

from openpyxl import load_workbook

from database.dbase import excel_to_db
from action.actions import name_convert, get_item_id


async def screen_excel(excel_path, excel_file):
    workbook = load_workbook(os.path.join(excel_path, excel_file), keep_vba=True)
    worksheet = workbook.worksheets[0]
    person = {}

    if excel_file.startswith("Заключение"):
        if len(workbook.sheetnames) > 1:
            sheet = workbook.worksheets[1]
            
            if (
                str(sheet["K1"].value) == "ФИО"
                and sheet["K3"].value
                and sheet["L3"].value
            ):
                person.update({"resume": await get_resume(sheet)})

        if sheet["C6"].value and sheet["C8"].value:
            person.update({"resume": await get_conclusion_resume(worksheet)})

        if sheet["C23"].value:
            person.update({"check": await get_check(worksheet)})

    else:
        person.update({"resume": await get_robot_resume(worksheet)})
        person.update({"robot": await get_robot(worksheet)})

    workbook.close()

    await excel_to_db(person)


async def get_resume(sheet):
    resume = {
        "fullname": name_convert(str(sheet["K3"].value)),
        "birthday": datetime.strptime(sheet["L3"].value, "%d.%m.%Y").date()
        if sheet["L3"].value
        else date.today(),
        "birthplace": str(sheet["M3"].value).strip(),
        "country": str(sheet["T3"].value).strip(),
        "snils": str(sheet["U3"].value).strip(),
        "inn": str(sheet["V3"].value).strip(),
    }
    return resume


async def get_conclusion_resume(sheet):
    resumes = {
        "fullname": name_convert(sheet["C6"].value),
        "birthday": (sheet["C8"].value).date()
        if isinstance(sheet["L3"].value, datetime)
        else date.today(),
    }
    return resumes


async def get_robot_resume(sheet):
    resumes = {
        "fullname": name_convert(sheet["B4"].value),
        "birthday": datetime.strptime(sheet["B5"].value, "%d.%m.%Y").date()
        if sheet["B5"].value
        else date.today(),
    }
    return resumes


async def get_check(sheet):
    checks = {
        "workplace": f"{sheet['C11'].value} - {sheet['D11'].value}; {sheet['C12'].value} - "
        f"{sheet['D12'].value}; {sheet['C13'].value} - {sheet['D13'].value}",
        "cronos": f"{sheet['B14'].value}: {sheet['C14'].value}; {sheet['B15'].value}: "
        f"{sheet['C15'].value}",
        "cros": sheet["C16"].value,
        "document": sheet["C17"].value,
        "debt": sheet["C18"].value,
        "bankruptcy": sheet["C19"].value,
        "bki": sheet["C20"].value,
        "affilation": sheet["C21"].value,
        "internet": sheet["C22"].value,
        "pfo": False
        if sheet["C26"].value or str(sheet["C26"].value).lower() == "не назначалось"
        else True,
        "addition": sheet["C28"].value,
        "conclusion": await get_item_id("conclusions", "conclusion", sheet["C23"].value),
        "deadline": datetime.now(),
        "officer": sheet["C25"].value,
    }
    return checks


async def get_robot(sheet):
    robot = {
        "employee": sheet["B27"].value,
        "terrorist": sheet["B17"].value,
        "inn": sheet["B18"].value,
        "bankruptcy": f"{sheet['B20'].value}, {sheet['B21'].value}, {sheet['B22'].value}",
        "mvd": sheet["B23"].value,
        "courts": sheet["B24"].value,
        "bki": sheet["B25"].value,
        "deadline": datetime.now(),
    }
    return robot
