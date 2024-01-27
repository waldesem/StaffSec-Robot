import os
import shutil
from datetime import datetime, date
import sqlite3

from openpyxl import load_workbook

from config import Config
from excelparser import ExcelFile, excel_to_db
from jsonparser import json_to_db


def main():
    now = datetime.now()

    main_file_date = date.fromtimestamp(os.path.getmtime(Config.MAIN_FILE))
    info_file_date = date.fromtimestamp(os.path.getmtime(Config.INFO_FILE))

    if date.today() in [main_file_date, info_file_date]:
        shutil.copy(os.path.join(Config.BASE_PATH, 'persons.db'), Config.ARCHIVE_DIR_2)
    if date.today() == main_file_date:
        shutil.copy(Config.MAIN_FILE, Config.ARCHIVE_DIR_2)
        parse_main()
    # if date.today() == info_file_date:
    #     shutil.copy(Config.INFO_FILE, Config.ARCHIVE_DIR_2)
    #     parse_info()        

    print(f'Script execution time: {datetime.now() - now}')


def parse_main():
    wb = load_workbook(Config.MAIN_FILE, keep_vba=True)
    ws = wb.worksheets[0]

    subdirs = os.listdir(Config.WORK_DIR)
    for i, cell in enumerate(ws['K10000':'K50000'], 10000):
        for c in cell:
            if c.value:
                if isinstance(c.value, datetime) and (c.value).date() == date.today():
                    fio = ExcelFile.fullname_parser(ws['B' + str(i)].value)
                    subdir = [sub for sub in subdirs if ExcelFile.fullname_parser(sub) == fio]
                    if subdir:
                        subdir_path = os.path.join(Config.WORK_DIR, subdir[0])

                        for file in os.listdir(subdir_path):
                            if (file.startswith("Заключение") or file.startswith("Результаты")) \
                                and (file.endswith("xlsm") or file.endswith("xlsx")):
                                excel_to_db(subdir_path, file)
                            elif file.endswith("json"):
                                json_to_db(subdir_path, file)

                        lnk = os.path.join(Config.ARCHIVE_DIR_2, 
                                           subdir[0][0], 
                                           f"{subdir[0]} - {ws['A' + str(i)].value}")
                        ws['L' + str(i)].hyperlink = str(lnk)
                        shutil.move(subdir_path, lnk)
                        
                        screen_registry_data(ws, i)

    wb.save(Config.MAIN_FILE)
    wb.close()

def parse_info():
    wb = load_workbook(Config.INFO_FILE, keep_vba=True, read_only=True)
    ws = wb.worksheets[0]
    for i, cell in enumerate(ws['G500':'G5000'], 500):
        for c in cell:
            if c.value:
                if isinstance(c.value, datetime) and (c.value).date() == date.today():
                    screen_iquiry_data(ws, i)
    wb.close()
        
def screen_iquiry_data(sheet, num): 
    info = sheet[f'E{num}'].value
    initiator = sheet[f'F{num}'].value
    fullname = ExcelFile.fullname_parser(sheet[f'A{num}'].value)
    birthday = (sheet[f'B{num}'].value).date() \
        if isinstance(sheet[f'B{num}'].value, datetime) \
            else date.today()
    
    connection = sqlite3.connect(Config.DATABASE_URI)
    with connection as conn:
        cursor = conn.cursor()

        person = cursor.execute(
            "SELECT * FROM persons WHERE fullname = ? AND birthday = ?", 
            (fullname, birthday)
        )
        result = person.fetchone()

        if not result:
            cursor.execute(
                "INSERT INTO persons (fullname, birthday, created, category_id, region_id, status_id) \
                            VALUES (?, ?, ?, ?, ?, ?)", 
                (fullname, birthday, datetime.now(), 1, 1, 9)
            )
            result = [cursor.lastrowid]
        else:
            cursor.execute(
                "UPDATE persons SET updated = ? WHERE id = ?", 
                (datetime.now(), result[0])
                )
        cursor.execute(
            "INSERT INTO inquiries (info, initiator, deadline, person_id) \
                        VALUES (?, ?, ?, ?)", 
            (info, initiator, datetime.now(), result[0])
            )
        conn.commit()


def screen_registry_data(sheet, num):
    fullname = ExcelFile.fullname_parser(sheet['B' + str(num)].value)
    birthday = (sheet['C' + str(num)].value).date() \
            if isinstance(sheet['C' + str(num)].value, datetime) \
                else date.today()
    decision = sheet[f'J{num}'].value
    url = sheet[f'L{num}'].value

    connection = sqlite3.connect(Config.DATABASE_URI)
    with connection as conn:
        cursor = conn.cursor()
        person = cursor.execute(
            "SELECT * FROM persons WHERE fullname = ? AND birthday = ?", 
            (fullname, birthday)
        )
        result = person.fetchone()
        if not result:
            cursor.execute(
                "INSERT INTO persons (fullname, birthday, path, created, category_id, region_id, status_id) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                (fullname, birthday, url, datetime.now(), 1, 1, 9)
                )

            cursor.execute(
                f"INSERT INTO checks (conclusion, deadline, person_id) VALUES (?, ?, ?)",
                (ExcelFile.get_conclusion_id(decision), datetime.now(), cursor.lastrowid)
                )
        else:
            cursor.execute(
                "UPDATE persons SET path = ?, updated = ? WHERE id = ?", 
                (url, datetime.now(), result[0])
                )
            cursor.execute(
                f"UPDATE checks SET conclusion = ?, deadline = ? WHERE person_id = ?", 
                (ExcelFile.get_conclusion_id(decision), datetime.now(), cursor.lastrowid)
                )
        conn.commit()
        

if __name__ == "__main__":
    main()
