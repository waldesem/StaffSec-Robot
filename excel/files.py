import os
import logging
import shutil
from datetime import datetime, date

from openpyxl import load_workbook

from config import Config
from parsers.excelparser import screen_excel
from parsers.jsonparser import screen_json
from database.dbase import db_iquiry_data, db_main_data
from action.actions import name_convert


"""Parses the main Excel file to get today's records, screens them, 
archives processed records, and saves results to the database.

- Loads the main Excel file 
- Iterates over today's records
    - Gets key data for the record
    - Finds the matching subdirectory
    - Screens Excel/JSON files in the subdirectory
    - Archives the subdirectory
    - Saves record data to the database
- Saves the updated main Excel file
"""
async def parse_main():
    wb = load_workbook(Config.MAIN_FILE, keep_vba=True)
    ws = wb.worksheets[0]

    subdirs = os.listdir(Config.WORK_DIR)
    for i, cell in enumerate(ws["K10000":"K50000"], 10000):
        for c in cell:
            if (
                c.value
                and isinstance(c.value, datetime)
                and (c.value).date() == date.today()
            ):
                fullname = name_convert(ws["B" + str(i)].value)
                birthday = (
                    (ws["C" + str(i)].value).date()
                    if isinstance(ws["C" + str(i)].value, datetime)
                    else date.today()
                )
                decision = ws[f"J{i}"].value
                lnk = ""

                for sub in subdirs:
                    if name_convert(sub) == fullname:
                        subdir_path = os.path.join(Config.WORK_DIR, sub)

                        for file in os.listdir(subdir_path):
                            if (
                                file.startswith("Заключение")
                                or file.startswith("Результаты")
                            ) and (file.endswith("xlsm") or file.endswith("xlsx")):
                                await screen_excel(subdir_path, file)
                            elif file.endswith("json"):
                                await screen_json(subdir_path, file)

                        lnk = os.path.join(
                            Config.ARCHIVE_DIR,
                            sub[0],
                            f"{sub} - {ws['A' + str(i)].value}",
                        )
                        ws["L" + str(i)].hyperlink = str(lnk)

                        try:
                            if not os.path.isdir(lnk):
                                shutil.move(subdir_path, lnk)
                                logging.info(f"{sub} moved to {Config.ARCHIVE_DIR}")
                            else:
                                logging.info(f"{sub} already in {Config.ARCHIVE_DIR}")
                        except Exception as e:
                            logging.error(e)

                        break

                await db_main_data(fullname, birthday, lnk)

    wb.save(Config.MAIN_FILE)
    wb.close()
    logging.info("Main file parsed")


"""Parse the inquiry worksheet in the info Excel file.

Iterates through the date column, checking for today's date. 
For each row with today's date, extracts the info, initiator, 
fullname, and birthday, and saves to the database.

After processing the whole worksheet, closes the workbook and logs 
that the info file was parsed.
"""
async def parse_inquiry():
    wb = load_workbook(Config.INFO_FILE, keep_vba=True)
    ws = wb.worksheets[0]
    for i, cell in enumerate(ws["G500":"G5000"], 500):
        for c in cell:
            if (
                c.value
                and isinstance(c.value, datetime)
                and (c.value).date() == date.today()
            ):
                info = ws[f"E{i}"].value
                initiator = ws[f"F{i}"].value
                fullname = name_convert(ws[f"A{i}"].value)
                birthday = (
                    (ws[f"B{i}"].value).date()
                    if isinstance(ws[f"B{i}"].value, datetime)
                    else date.today()
                )
                await db_iquiry_data(info, initiator, fullname, birthday)
    wb.close()
    logging.info("Info file parsed")
