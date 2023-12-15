import os
import shutil
from datetime import date

from config import Config
from .parsers.parser import Parser


class Main:
    """Initialize class for checking date of file changes"""

    def __init__(self):
        self.main_file_date = date.fromtimestamp(os.path.getmtime(Config.MAIN_FILE))
        self.info_file_date = date.fromtimestamp(os.path.getmtime(Config.INFO_FILE))
        self.check_date()

    def check_date(self):   # check file changing date
        if self.main_file_date == date.today() or self.info_file_date == date.today():
            for file in (Config.DATABASE_URI, Config.MAIN_FILE,  Config.INFO_FILE):
                shutil.copy(file, Config.ARCHIVE_DIR)
            parse = Parser()
            parse(self.main_file_date, self.info_file_date)
        

if __name__ == "__main__":
    Main()
