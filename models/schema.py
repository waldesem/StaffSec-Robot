import re
from datetime import datetime

from marshmallow import Schema, fields, post_dump
    

class PersonSchema(Schema):
    id = fields.Int()
    region_id = fields.Int(default = 1)
    category_id = fields.Int(default = 1)
    fullname = fields.Str(attribute="full_name")
    previous = fields.Str(attribute="last_name")
    birthday = fields.Str()
    birthplace = fields.Str(attribute="birth_place")
    country = fields.Str()
    snils = fields.Str()
    inn = fields.Str()
    education = fields.Str()
    status_id = fields.Int(default = 9)

    @post_dump
    def birthday_handler(self, data, **kwargs):
        if isinstance(data['birthday'], str) and re.match('\d{4}-\d{2}-\d{2}', data['birthday']):
            try:
                data['birthday'] = datetime.strptime(data['birthday'], '%Y-%m-%d').date()
            except ValueError:
                data['birthday'] = datetime.strptime("1900-01-01", '%Y-%m-%d').date()
        else:
            data['birthday'] = datetime.strptime("1900-01-01", '%Y-%m-%d').date()
        return data
        

class CheckSchema(Schema):
    id = fields.Int()
    workplace = fields.Str(attribute="check_work_place")
    document = fields.Str(attribute="check_passport")
    debt = fields.Str(attribute="check_debt")
    bankruptcy = fields.Str(attribute="check_bankruptcy")
    bki = fields.Str(attribute="check_bki")
    affiliation = fields.Str(attribute="check_affiliation")
    internet = fields.Str(attribute="check_internet")
    cronos = fields.Str(attribute="check_cronos")
    cros = fields.Str(attribute="check_cross")
    conclusion_id = fields.Str(attribute="resume")
    officer = fields.Str()
    deadline = fields.Str(attribute="date_check")
    person_id = fields.Str(attribute="check_id")

    @post_dump
    def date_check_handler(self, data, **kwargs):
        if isinstance(data['deadline'], str) and re.match('\d{4}-\d{2}-\d{2}', data['deadline']):
            try:
                data['deadline'] = datetime.strptime(data['deadline'], '%Y-%m-%d').date()
            except ValueError:
                data['deadline'] = datetime.strptime("1900-01-01", '%Y-%m-%d').date()
        else:
            data['deadline'] = datetime.strptime("1900-01-01", '%Y-%m-%d').date()
        return data
    
    @post_dump
    def conclusion_handler(self, data, **kwargs):
        if data['conclusion_id']:
            if data['conclusion_id'].lower() in ['СОГЛАСОВАНО С КОММЕНТАРИЕМ'.lower(), 
                                            'С КОММЕНТАРИЕМ'.lower()]:
                data['conclusion_id'] = 2
            elif data['conclusion_id'].lower() in ['ОТКАЗАНО В СОГЛАСОВАНИИ'.lower(), 
                                            'ОТКАЗ'.lower(),
                                            'НЕГАТИВ'.lower(),
                                            '']:
                data['conclusion_id'] = 3
            else:
                data['conclusion_id'] = 1
        else:
            data['conclusion_id'] = 1
        return data
            

class InquirySchema(Schema):
    id = fields.Int()
    info = fields.Str()
    initiator = fields.Str(attribute="firm")
    deadline = fields.Str(attribute="date_inq")
    person_id = fields.Int(attribute="iquery_id")
    
    @post_dump
    def date_inq_handler(self, data, **kwargs):
        if isinstance(data['deadline'], str) and re.match('\d{4}-\d{2}-\d{2}', data['deadline']):
            try:
                data['deadline'] = datetime.strptime(data['deadline'], '%Y-%m-%d').date()
            except ValueError:
                data['deadline'] = datetime.strptime("1900-01-01", '%Y-%m-%d').date()
        else:
            data['deadline'] = datetime.strptime("1900-01-01", '%Y-%m-%d').date()
        return data
        
    
class StaffSchema(Schema):
    position = fields.Str(attribute="staff")
    department = fields.Str()
    person_id = fields.Int(attribute="id")


class DocumentSchema(Schema):
    view = fields.Str(default="Паспорт")
    series = fields.Str(attribute="series_passport")
    number = fields.Str(attribute="number_passport")
    issue = fields.Str(attribute='date_given')
    person_id = fields.Int(attribute="id")

    @post_dump
    def date_given_handler(self, data, **kwargs):
        if isinstance(data['issue'], str) and re.match('\d{4}-\d{2}-\d{2}', data['issue']):
            try:
                data['issue'] = datetime.strptime(data['issue'], '%Y-%m-%d').date()
            except ValueError:
                data['issue'] = datetime.strptime("1900-01-01", '%Y-%m-%d').date()
        else:
            data['issue'] = datetime.strptime("1900-01-01", '%Y-%m-%d').date()
        return data
            
            
class RegAddressSchema(Schema):
    view = fields.Str(default="Адрес регистрации")
    address = fields.Str(attribute="reg_address")
    person_id = fields.Int(attribute="id")


class LiveAddressSchema(Schema):
    view = fields.Str(default="Адрес проживания")
    address = fields.Str(attribute="live_address")
    person_id = fields.Int(attribute="id")


class PhoneContactSchema(Schema):
    view = fields.Str(default="Телефон")
    contact = fields.Str(attribute="phone")
    person_id = fields.Int(attribute="id")


class EmailContactSchema(Schema):
    view = fields.Str(default="Электронная почта")
    contact = fields.Email(attribute="email")
    person_id = fields.Int(attribute="id")


class PathSchema(Schema):
    path = fields.Str(attribute="url")
    registry_id = fields.Int()


class ConcludeSchema(Schema):
    conclusion = fields.Str()
    id = fields.Int()