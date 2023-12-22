from datetime import datetime

from typing import List
from sqlalchemy import Boolean, create_engine, ForeignKey, String, Text, Date, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from config import Config
from models.classes import Conclusions


engine = create_engine(Config.DATABASE_URI, echo=True)


def default_time():
    return datetime.now()


class Base(DeclarativeBase):
    
    __abstract__ = True


class Category(Base):

    __tablename__ = 'categories'
    
    id: Mapped[int] = mapped_column(nullable=False, unique=True, primary_key=True, autoincrement=True)
    category: Mapped[str] = mapped_column(String(255))
    persons: Mapped[List['Person']] = relationship(back_populates='categories')

    def get_id(self, category):
        with engine.connect() as conn:
            result = conn.execute(
                select(Category.id)
                .filter(Category.category == category)
                ).scalar_one_or_none()
        return result


class Status(Base):
    
    __tablename__ = 'statuses'
    
    id: Mapped[int] = mapped_column(nullable=False, unique=True, primary_key=True, autoincrement=True)
    status: Mapped[str] = mapped_column(String(255))
    persons: Mapped[List['Person']] = relationship(back_populates='statuses')

    def get_id(self, status):
        with engine.connect() as conn:
            result = conn.execute(
                select(Status.id)
                .filter(Status.status == status)
                ).scalar_one_or_none()
        return result
    

class Region(Base):
    """ Create model for regions"""

    __tablename__ = 'regions'
    
    id: Mapped[int] = mapped_column(nullable=False, unique=True, primary_key=True, autoincrement=True)
    region: Mapped[str] = mapped_column(String(255))
    persons : Mapped[List['Person']] = relationship(back_populates='regions')
   
    def get_id(self, region):
        with engine.connect() as conn:
            result = conn.execute(
                select(Region.id)
                .filter(Region.region == region)
                ).scalar_one_or_none()
        return result
    

class Person(Base):
    """ Create model for persons dates"""

    __tablename__ = 'persons'

    id: Mapped[int] = mapped_column(nullable=False, unique=True, primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'))
    region_id: Mapped[int] = mapped_column(ForeignKey('regions.id'))
    fullname: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    previous: Mapped[str] = mapped_column(Text)
    birthday: Mapped[datetime] = mapped_column(Date, nullable=False, index=True)
    birthplace: Mapped[str] = mapped_column(Text)
    country: Mapped[str] = mapped_column(String(255))
    ext_country: Mapped[str] = mapped_column(String(255))
    snils: Mapped[str] = mapped_column(String(11))
    inn: Mapped[str] = mapped_column(String(12))
    education: Mapped[str] = mapped_column(Text)
    marital: Mapped[str] = mapped_column(String(255))
    addition: Mapped[str] = mapped_column(Text)
    path: Mapped[str] = mapped_column(Text)
    status_id: Mapped[int] = mapped_column(ForeignKey('statuses.id'))
    create: Mapped[datetime] = mapped_column(Date, default=default_time)
    update: Mapped[datetime] = mapped_column(Date, onupdate=default_time)
    staffs: Mapped[List['Staff']] = relationship(
        back_populates='persons', cascade="all, delete, delete-orphan"
        )
    documents: Mapped[List['Document']] = relationship(
        back_populates='persons', cascade="all, delete, delete-orphan"
        )
    addresses: Mapped[List['Address']] = relationship(
        back_populates='persons', cascade="all, delete, delete-orphan"
        )
    workplaces: Mapped[List['Workplace']] = relationship(
        back_populates='persons', cascade="all, delete, delete-orphan"
        )
    contacts: Mapped[List['Contact']] = relationship(
        back_populates='persons', cascade="all, delete, delete-orphan"
        )
    checks: Mapped[List['Check']] = relationship(
        back_populates='persons', cascade="all, delete, delete-orphan"
        )
    robots: Mapped[List['Robot']] = relationship(
        back_populates='persons', cascade="all, delete, delete-orphan"
        )
    inquiries: Mapped[List['Inquiry']] = relationship(
        back_populates='persons', cascade="all, delete, delete-orphan"
        )
    affilations: Mapped[List['Affilation']] = relationship(
        back_populates='persons', cascade="all, delete, delete-orphan"
        )
    categories: Mapped['Category'] = relationship(back_populates='persons')
    statuses: Mapped['Status'] = relationship(back_populates='persons')
    regions: Mapped['Region'] = relationship(back_populates='persons')


class Staff(Base):
    """ Create model for staff"""

    __tablename__ = 'staffs'

    id: Mapped[int] = mapped_column(nullable=False, unique=True, primary_key=True, autoincrement=True)
    position: Mapped[str] = mapped_column(Text)
    department: Mapped[str] = mapped_column(Text)
    person_id: Mapped[int] = mapped_column(ForeignKey('persons.id'))
    persons: Mapped[List['Person']] = relationship(back_populates='staffs')


class Document(Base):
    """ Create model for Document dates"""

    __tablename__ = 'documents'

    id: Mapped[int] = mapped_column(nullable=False, unique=True, primary_key=True, autoincrement=True)

    view: Mapped[str] = mapped_column(String(255))
    series: Mapped[str] = mapped_column(String(255))
    number: Mapped[str] = mapped_column(String(255))
    agency: Mapped[str] = mapped_column(Text)
    issue: Mapped[datetime] = mapped_column(Date)
    person_id: Mapped[int] = mapped_column(ForeignKey('persons.id'))
    persons: Mapped[List['Person']] = relationship(back_populates='documents')


class Address(Base): 
    """ Create model for addresses"""

    __tablename__ = 'addresses'

    id: Mapped[int] = mapped_column(nullable=False, unique=True, primary_key=True, autoincrement=True)
    view: Mapped[str] = mapped_column(String(255))
    region: Mapped[str] = mapped_column(String(255))
    address: Mapped[str] = mapped_column(Text)
    person_id: Mapped[int] = mapped_column(ForeignKey('persons.id'))
    persons: Mapped[List['Person']] = relationship(back_populates='addresses')


class Contact(Base):
    """ Create model for contacts"""

    __tablename__ = 'contacts'

    id: Mapped[int] = mapped_column(nullable=False, unique=True, primary_key=True, autoincrement=True)
    view: Mapped[str] = mapped_column(String(255))
    contact: Mapped[str] = mapped_column(String(255))
    person_id: Mapped[int] = mapped_column(ForeignKey('persons.id'))
    persons: Mapped[List['Person']] = relationship(back_populates='contacts')


class Workplace(Base):
    """ Create model for workplaces"""

    __tablename__ = 'workplaces'

    id: Mapped[int] = mapped_column(nullable=False, unique=True, primary_key=True, autoincrement=True)
    start_date: Mapped[datetime] = mapped_column(Date)
    end_date: Mapped[datetime] = mapped_column(Date)
    workplace: Mapped[str] = mapped_column(String(255))
    address: Mapped[str] = mapped_column(Text)
    position: Mapped[str] = mapped_column(Text)
    reason: Mapped[str] = mapped_column(Text)
    person_id: Mapped[int] = mapped_column(ForeignKey('persons.id'))
    persons: Mapped[List['Person']] = relationship(back_populates='workplaces')


class Affilation(Base):
    """ Create model for affilations"""

    __tablename__ = 'affilations'

    id: Mapped[int] = mapped_column(nullable=False, unique=True, primary_key=True, autoincrement=True)
    view: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(Text)
    inn: Mapped[str] = mapped_column(String(255))
    position: Mapped[str] = mapped_column(Text)
    deadline: Mapped[datetime] = mapped_column(Date, default=default_time)
    person_id: Mapped[int] = mapped_column(ForeignKey('persons.id'))
    persons: Mapped[List['Person']] = relationship(back_populates='affilations')


class Check(Base):
    """ Create model for persons checks"""

    __tablename__ = 'checks'

    id: Mapped[int] = mapped_column(nullable=False, unique=True, primary_key=True, autoincrement=True)
    workplace: Mapped[str] = mapped_column(Text)
    document: Mapped[str] = mapped_column(Text)
    inn: Mapped[str] = mapped_column(Text)
    debt: Mapped[str] = mapped_column(Text)
    bankruptcy: Mapped[str] = mapped_column(Text)
    bki: Mapped[str] = mapped_column(Text)
    courts: Mapped[str] = mapped_column(Text)
    affiliation: Mapped[str] = mapped_column(Text)
    terrorist: Mapped[str] = mapped_column(Text)
    mvd: Mapped[str] = mapped_column(Text)
    internet: Mapped[str] = mapped_column(Text)
    cronos: Mapped[str] = mapped_column(Text)
    cros: Mapped[str] = mapped_column(Text)
    addition: Mapped[str] = mapped_column(Text)
    pfo: Mapped[bool] = mapped_column(Boolean)
    comments: Mapped[str] = mapped_column(Text)
    conclusion: Mapped[int] = mapped_column(ForeignKey('conclusions.id'))
    officer: Mapped[str] = mapped_column(String(255))
    deadline: Mapped[datetime] = mapped_column(Date, default=default_time, 
                         onupdate=default_time)
    person_id: Mapped[int] = mapped_column(ForeignKey('persons.id'))
    persons: Mapped[List['Person']] = relationship(back_populates='checks')
    conclusions: Mapped['Conclusion'] = relationship(back_populates='checks')


class Conclusion(Base):
    
    __tablename__ = 'conclusions'
    
    id: Mapped[int] = mapped_column(nullable=False, unique=True, primary_key=True, autoincrement=True)
    conclusion: Mapped[str] = mapped_column(String(255))
    checks: Mapped[List['Check']] = relationship(back_populates='conclusions')

    def get_id(self, conclusion):
        with engine.connect() as conn:
            mapped = {
                'согласовано': Conclusions.agreed.value,
                'с комментарием': Conclusions.with_comment.value,
                'отказ': Conclusions.denied.value
            }
            result = conn.execute(
            select(Conclusion)
            .filter(Conclusion.conclusion == mapped.get(conclusion.lower(), Conclusions.canceled.value))
            ).scalar_one_or_none().id
            return result


class Robot(Base):
    """ Create model for robots"""

    __tablename__ = 'robots'

    id: Mapped[int] = mapped_column(nullable=False, unique=True, primary_key=True, autoincrement=True)
    employee: Mapped[str] = mapped_column(Text)
    inn: Mapped[str] = mapped_column(Text)
    bankruptcy: Mapped[str] = mapped_column(Text)
    bki: Mapped[str] = mapped_column(Text)
    courts: Mapped[str] = mapped_column(Text)
    terrorist: Mapped[str] = mapped_column(Text)
    mvd: Mapped[str] = mapped_column(Text)
    deadline: Mapped[datetime] = mapped_column(Date, default=default_time)
    person_id: Mapped[int] = mapped_column(ForeignKey('persons.id'))
    persons: Mapped[List['Person']] = relationship(back_populates='robots')


class Inquiry(Base):
    """ Create model for persons inquiries"""

    __tablename__ = 'inquiries'

    id: Mapped[int] = mapped_column(nullable=False, unique=True, primary_key=True, autoincrement=True)
    info: Mapped[str] = mapped_column(Text)
    initiator: Mapped[str] = mapped_column(String(255))
    source: Mapped[str] = mapped_column(String(255))
    officer: Mapped[str] = mapped_column(String(255))
    deadline: Mapped[datetime] = mapped_column(Date, default=default_time)
    person_id: Mapped[int] = mapped_column(ForeignKey('persons.id'))
    persons: Mapped[List['Person']] = relationship(back_populates='inquiries')


class Connect(Base):
    """ Create model for persons connects"""
    
    __tablename__ = 'connects'

    id: Mapped[int] = mapped_column(nullable=False, unique=True, primary_key=True, autoincrement=True)
    company: Mapped[str] = mapped_column(String(255))
    city: Mapped[str] = mapped_column(String(255))
    fullname: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(255))
    adding: Mapped[str] = mapped_column(String(255))
    mobile: Mapped[str] = mapped_column(String(255))
    mail: Mapped[str] = mapped_column(String(255))
    comment: Mapped[str] = mapped_column(Text)
    data: Mapped[datetime] = mapped_column(Date, default=default_time, onupdate=default_time)
