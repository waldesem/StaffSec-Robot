from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import create_engine, Column, Integer, Text, ForeignKey


_engine = create_engine('sqlite:///' + '/home/semenenko/MyProjects/personal.db')


class Base(DeclarativeBase):
    __abstract__ = True


class Candidate(Base):
    """ Create model for candidates dates"""

    __tablename__ = 'candidates'

    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    staff = Column(Text)
    department = Column(Text)
    full_name = Column(Text, index=True)
    last_name = Column(Text)
    birthday = Column(Text)
    birth_place = Column(Text)
    country = Column(Text)
    series_passport = Column(Text)
    number_passport = Column(Text)
    date_given = Column(Text)
    snils = Column(Text)
    inn = Column(Text)
    reg_address = Column(Text)
    live_address = Column(Text)
    phone = Column(Text)
    email = Column(Text)
    education = Column(Text)
    check = relationship('Check', cascade="all, delete", back_populates='candidate')
    inquery = relationship('Inquery', cascade="all, delete", back_populates='candidate')
    registr = relationship('Registr', cascade="all, delete", back_populates='candidate')


class Check(Base):
    """ Create model for candidates checks"""

    __tablename__ = 'checks'

    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    check_work_place = Column(Text)
    check_passport = Column(Text)
    check_debt = Column(Text)
    check_bankruptcy = Column(Text)
    check_bki = Column(Text)
    check_affiliation = Column(Text)
    check_internet = Column(Text)
    check_cronos = Column(Text)
    check_cross = Column(Text)
    resume = Column(Text)
    date_check = Column(Text)
    officer = Column(Text)
    check_id = Column(Integer, ForeignKey('candidates.id'))
    candidate = relationship('Candidate', back_populates='check')


class Inquery(Base):
    """ Create model for candidates iqueries"""

    __tablename__ = 'iqueries'

    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    staff = Column(Text)
    period = Column(Text)
    info = Column(Text)
    firm = Column(Text)
    date_inq = Column(Text)
    iquery_id = Column(Integer, ForeignKey('candidates.id'))
    candidate = relationship('Candidate', back_populates='inquery')


class Registr(Base):
    """ Create model for candidates iqueries"""

    __tablename__ = 'registries'

    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    checks = Column(Text)
    recruiter = Column(Text)
    fin_decision = Column(Text)
    final_date = Column(Text)
    url = Column(Text)
    registry_id = Column(Integer, ForeignKey('candidates.id'))
    candidate = relationship('Candidate', back_populates='registr')

Base.metadata.drop_all(_engine)
Base.metadata.create_all(_engine)
