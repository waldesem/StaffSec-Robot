import os


class Config:

    BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    WORK_DIR = os.path.join(BASE_PATH, 'Кандидаты')
    ARCHIVE_DIR = os.path.join(BASE_PATH, 'Персонал')
    ARCHIVE_DIR_2 = os.path.join(ARCHIVE_DIR, 'Персонал-2')
    MAIN_FILE = os.path.join(WORK_DIR, 'Кандидаты.xlsm')
    INFO_FILE = os.path.join(WORK_DIR, 'Запросы по работникам.xlsx')
    DATABASE_URI = 'sqlite:///' + os.path.join(BASE_PATH, 'test.db')
