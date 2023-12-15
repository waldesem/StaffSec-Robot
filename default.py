import os

from sqlalchemy.orm import Session

from config import Config
from models.model import Base, Region, Status, Conclusion, Category, engine
from models.classes import Regions, Statuses, Conclusions, Categories


def create_default():
    """Create default values"""
    base_path = os.path.join(Config.BASE_PATH)
    if not os.path.isdir(base_path):
        os.mkdir(base_path)
    print('Directory BASE_PATH created')
    
    for letter in 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ':
        letter_path = os.path.join(Config.BASE_PATH, letter)
        if not os.path.isdir(letter_path):
            os.mkdir(letter_path)
    print(f'Alphabet directories created')
    
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    
    with Session(engine) as session:
        session.add_all([Region(region=reg.name) for reg in Regions])
        session.add_all([Status(status=item.name) for item in Statuses])
        session.add_all([Conclusion(conclusion=item.name) for item in Conclusions])
        session.add_all([Category(category=item.name) for item in Categories])
        session.commit()
    print('Models created and filled')

if __name__ == '__main__':
    create_default()
