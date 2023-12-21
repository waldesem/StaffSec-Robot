import os
import argparse

from config import Config


"""Parse command line arguments"""
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--create', action='store_true', help='Create default values')
parser.add_argument('-d', '--deprecate', action='store_true', help='Create deprecated values')
args = parser.parse_args()


def create():
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


if __name__ == '__main__':
    if args.create:
        create()
    else:
        parser.print_help()