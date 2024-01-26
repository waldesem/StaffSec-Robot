import os
import shutil
from datetime import datetime, date
import sqlite3

from openpyxl import load_workbook

from config import Config
from excelparser import excel_to_db
from jsonparser import json_to_db


def main():
    main_file_date = date.fromtimestamp(os.path.getmtime(Config.MAIN_FILE))
    info_file_date = date.fromtimestamp(os.path.getmtime(Config.INFO_FILE))
    if date.today() in [main_file_date, info_file_date]:
        shutil.copy(os.path.join(Config.BASE_PATH, 'persons.db'), Config.ARCHIVE_DIR_2)
    if date.today() == info_file_date:
        shutil.copy(Config.INFO_FILE, Config.ARCHIVE_DIR_2)
        parse_main()
    if date.today() == main_file_date:
        shutil.copy(Config.MAIN_FILE, Config.ARCHIVE_DIR_2)
        parse_info()        


def parse_main():
    wb = load_workbook(Config.MAIN_FILE, keep_vba=True, read_only=False)
    ws = wb.worksheets[0]

    subdirs = os.listdir(Config.WORK_DIR)
    for i, cell in enumerate(ws['K10000':'K50000'], 10000):
        for c in cell:
            if c.value:
                if isinstance(c.value, datetime) and (c.value).date() == date.today():
                    fio = ws['B' + str(i)].value.strip()
                    subdir = [sub for sub in subdirs if sub.lower().strip() == fio.lower()]
                    if len(subdir):
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

def parse_info():
    wb = load_workbook(Config.INFO_FILE, keep_vba=True)
    ws = wb.worksheets[0]
    for i, cell in enumerate(ws['G500':'G5000']):
        for c in cell:
            if c.value:
                if isinstance(c.value, datetime) and (c.value).date() == date.today():
                    screen_iquiry_data(ws, i)
    wb.close()
        
def screen_iquiry_data(sheet, num): 
    chart = {
        'info': sheet[f'E{num}'].value,
        'initiator': sheet[f'F{num}'].value,
        'fullname': sheet[f'A{num}'].value,
        'deadline': date.today(),
        'birthday': sheet[f'B{num}'].value \
            if isinstance(sheet[f'B{num}'].value, datetime) \
                else date.today()
        }
    connection = sqlite3.connect(Config.DATABASE_URI)
    with connection as conn:
        cursor = conn.cursor()
        person = cursor.execute(
            "SELECT * FROM persons WHERE fullname = ? AND birthday = ?", 
            (chart['fullname'], chart['birthday'])
        )
        result = person.fetchone()
        print(result)
        if not result:
            cursor.execute("INSERT INTO persons (fullname, birthday, created, category_id, region_id, status_id) \
                            VALUES (?, ?, ?, ?, ?, ?)", (chart['fullname'], chart['birthday'],
                                                chart['deadline'], 1, 1, 9))
        else:
            cursor.execute("UPDATE persons SET update = ? WHERE id = ?", 
                            date.today(), result[0])
        cursor.execute("INSERT INTO inquiries (info, initiator, deadline, person_id) \
                        VALUES (?, ?, ?, ?)", 
                        (chart['info'], chart['initiator'], date.today(), result[0]))
        conn.commit()


def screen_registry_data(sheet, num):
    chart = {'fullname': sheet['A' + str(num)].value,
                'birthday': (sheet['B' + str(num)].value).date() \
                if isinstance(sheet['B' + str(num)].value, datetime)
                    else date.today(),
                'decision': sheet[f'J{num}'].value,
                'deadline': date.today(),
                'url': sheet[f'L{num}'].value}

    connection = sqlite3.connect(Config.DATABASE_URI)
    with connection as conn:
        cursor = conn.cursor()
        person = cursor.execute(
            "SELECT * FROM persons WHERE fullname = ? AND birthday = ?", 
            (chart['fullname'], chart['birthday'])
        )
        result = person.fetchone()
        if not result:
            cursor.execute("INSERT INTO persons (fullname, birthday, path) VALUES (?, ?, ?)", 
                            (chart['fullname'], chart['birthday'], chart['url']))

            cursor.execute(f"UPDATE checks SET conclusion = ?, deadline = ?, person_id = ?", 
                            (get_conclusion_id(chart['decision']), 
                            chart['deadline'], cursor.lastrowid))
        else:
            cursor.execute("UPDATE persons SET path = ? WHERE id = ?", 
                            (chart['url'], result[0]))
        conn.commit()

def get_conclusion_id(name):
        connection = sqlite3.connect(Config.DATABASE_URI)
        with connection as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM conclusions WHERE LOWER (conclusion) = ?",
                (name.lower(), )
            )
            result = cursor.fetchone()
            return result[0] if result else 1
        

if __name__ == "__main__":
    main()
