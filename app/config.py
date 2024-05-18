import os


class Config:

    BASE_PATH = r"\\cronosx1\New folder\УВБ\Отдел корпоративной защиты"
    WORK_DIR = os.path.join(BASE_PATH, 'Кандидаты')
    ARCHIVE_DIR = os.path.join(BASE_PATH, 'Персонал', 'Персонал-2')
    MAIN_FILE = os.path.join(WORK_DIR, 'Кандидаты.xlsm')
    INFO_FILE = os.path.join(WORK_DIR, 'Запросы по работникам.xlsx')
    DATABASE_URI = os.path.join(BASE_PATH, 'persons.db')
    LOG_FILE = os.path.join(BASE_PATH, 'robot.log')
