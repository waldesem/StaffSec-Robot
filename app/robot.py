from datetime import date
import logging
import shutil

from config import Config
from action.actions import get_file_timestamp
from excel.files import parse_registry


logging.basicConfig(
    filename=Config.LOG_FILE,
    filemode="w",
    format="%(asctime)s - %(message)s",
    level=logging.INFO,
)


def main():
    logging.info("Script start")
    if date.today() in [
        get_file_timestamp(Config.MAIN_FILE),
        get_file_timestamp(Config.INFO_FILE),
    ]:
        for file in [
            Config.MAIN_FILE,
            Config.INFO_FILE,
        ]:
            try:
                shutil.copy(file, Config.ARCHIVE_DIR)
                logging.info(f"{file} backuped")
                parse_registry(file)
            except Exception as e:
                logging.error(e)

        logging.info("Script executed")
    else:
        logging.info("Files not changed")


if __name__ == "__main__":
    main()
