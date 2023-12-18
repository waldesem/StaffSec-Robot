import os
import argparse

from sqlalchemy.orm import Session

from config import Config
from models.model import Base, Region, Status, Conclusion, Category, engine
from models.classes import Regions, Statuses, Conclusions, Categories


"""Parse command line arguments"""
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--create', action='store_true', help='Create default values')
args = parser.parse_args()


def create_default():
    """Create default values"""
    if not os.path.isdir(Config.WORK_DIR):
        os.mkdir(Config.WORK_DIR)
    print('Directory WORK_DIR created')

    if not os.path.isdir(Config.ARCHIVE_DIR):
        os.mkdir(Config.ARCHIVE_DIR)
    print('Directory ARCHIVE_DIR created')

    if not os.path.isdir(Config.ARCHIVE_DIR_2):
        os.mkdir(Config.ARCHIVE_DIR_2)
    print('Directory ARCHIVE_DIR_2 created')

    for letter in 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ':
        letter_path = os.path.join(Config.ARCHIVE_DIR_2, letter)
        if not os.path.isdir(letter_path):
            os.mkdir(letter_path)
    print(f'Alphabet directories created')

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        session.add_all([Region(region=reg.value) for reg in Regions])
        session.add_all([Status(status=item.value) for item in Statuses])
        session.add_all([Conclusion(conclusion=item.value) for item in Conclusions])
        session.add_all([Category(category=item.value) for item in Categories])
        session.commit()
    print('Models created and filled')


if __name__ == '__main__':
    if args.create:
        create_default()
    else:
        print('Nothing to do')