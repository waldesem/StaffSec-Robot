from datetime import datetime

from marshmallow import Schema, fields, pre_load


class PersonSchema(Schema):
    id: fields.Int()
    region_id: fields.Int(default = 1)
    category_id: fields.Int(default = 1)
    fullname: fields.Str(attribute="full_name")
    previous: fields.Str(attribute="last_name")
    birthday: fields.Date()
    birthplace: fields.Str(attribute="birth_place")
    country: fields.Str()
    snils: fields.Str()
    inn: fields.Str()
    education: fields.Str()
    status_id: fields.Int()
    create: fields.Date(default = datetime.now())

class StaffSchema(Schema):
    positon = fields.Str(attribute="staff")
    department = fields.Str()
    person_id = fields.Int(attribute="id")


class DocumentSchema(Schema):
    view = fields.Str(default="Паспорт")
    series = fields.Str(attribute="series_passport")
    number = fields.Str(attribute="number_passport")
    issue = fields.Date(atttribute='date_given')
    person_id = fields.Int(attribute="id")

    @pre_load
    def format_date(self, data):
        data['date_given'] = datetime.strptime(data['date_given'], "%d.%m.%Y")
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
    contact = fields.Str(attribute="email")
    person_id = fields.Int(attribute="id")


class PathSchema(Schema):
    path = fields.Str(attribute="url")
    registry_id = fields.Int()
