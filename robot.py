import os
import shutil
from datetime import datetime, date
import logging

from config import Config
from excel.files import parse_inquiry, parse_main


logging.basicConfig(
    filename=Config.LOG_FILE, format="%(asctime)s - %(message)s", level=logging.INFO
)


def main():
    now = datetime.now()

    main_file_date = date.fromtimestamp(os.path.getmtime(Config.MAIN_FILE))
    info_file_date = date.fromtimestamp(os.path.getmtime(Config.INFO_FILE))

    if date.today() in [main_file_date, info_file_date]:
        for file in [Config.MAIN_FILE, Config.INFO_FILE, Config.DATABASE_URI]:
            try:
                shutil.copy(file, Config.ARCHIVE_DIR)
                logging.info(f"{file} backuped")
            except Exception as e:
                logging.error(e)

        parse_main(Config.MAIN_FILE),
        parse_inquiry(Config.INFO_FILE),

    else:
        logging.info("Files not changed")

    logging.info(f"Script execution time: {datetime.now() - now}")


if __name__ == "__main__":
    main()
