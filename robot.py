import os
import shutil
from datetime import datetime, date
import logging
import asyncio

from config import Config
from excel.files import parse_inquiry, parse_main


logging.basicConfig(
    filename=Config.LOG_FILE, format="%(asctime)s - %(message)s", level=logging.INFO
)


async def main():
    now = datetime.now()

    main_file_date = date.fromtimestamp(os.path.getmtime(Config.MAIN_FILE))
    info_file_date = date.fromtimestamp(os.path.getmtime(Config.INFO_FILE))

    tasks = [
        archive_db(main_file_date, info_file_date),
        archive_main(main_file_date),
        archive_info(info_file_date),
    ]
    await asyncio.gather(*tasks)

    logging.info(f"Script execution time: {datetime.now() - now}")


async def archive_db(main_file_date, info_file_date):
    if date.today() in [main_file_date, info_file_date]:
        try:
            shutil.copy(os.path.join(Config.BASE_PATH, "persons.db"), Config.ARCHIVE_DIR)
            logging.info(f"persons.db copied to {Config.ARCHIVE_DIR}")
        except Exception as e:
            logging.error(e)
    else:
        logging.info(f"persons.db not changed")


async def archive_main(main_file_date):
    if date.today() == main_file_date:
        try:
            shutil.copy(Config.MAIN_FILE, Config.ARCHIVE_DIR)
            logging.info(f"Main file copied to {Config.ARCHIVE_DIR}")
            await parse_main()
        except Exception as e:
            logging.error(e)
    else:
        logging.info(f"Main file not changed")


async def archive_info(info_file_date):
    if date.today() == info_file_date:
        try:
            shutil.copy(Config.INFO_FILE, Config.ARCHIVE_DIR)
            logging.info(f"Info file copied to {Config.ARCHIVE_DIR}")
            await parse_inquiry()
        except Exception as e:
            logging.error(e)
    else:
        logging.info(f"Info file not changed")


if __name__ == "__main__":
    asyncio.run(main())
