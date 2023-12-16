import os
import shutil
from datetime import date

from config import Config
from parsers.parser import parse_main, parse_info


def main():
    main_file_date = date.fromtimestamp(os.path.getmtime(Config.MAIN_FILE))
    info_file_date = date.fromtimestamp(os.path.getmtime(Config.INFO_FILE))
    if date.today() == main_file_date or date.today() == info_file_date:
        shutil.copy(Config.DATABASE_URI, Config.ARCHIVE_DIR)
    if date.today() == info_file_date:
        shutil.copy(Config.INFO_FILE, Config.ARCHIVE_DIR)
        parse_main()
    if date.today() == main_file_date:
        shutil.copy(Config.MAIN_FILE, Config.ARCHIVE_DIR)
        parse_info()        


if __name__ == "__main__":
    main()
