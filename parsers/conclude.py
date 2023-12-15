from datetime import datetime
import openpyxl
from database import *

class Forms:
    """Объявляем класс Forms для работы с данными"""

    resume = None
    last_names = None
    passports = None
    address = None
    works = None
    contacts = None
    staffs = None
    checks = None

    def __init__(self, path):
        self.book = openpyxl.load_workbook(path, keep_vba=True)
        self.sheet = None

    def check_excel(self):  # parse Excel files with conclusions and resume dates
        self.sheet = self.book.worksheets[0]
        self.get_check()
        flag = None
        if len(self.book.sheetnames) > 1:
            sheet = self.book.worksheets[1]
            if str(sheet['K1'].value) == 'ФИО':
                self.sheet = sheet
                self.get_resume()
                self.get_last_names()
                self.get_passport()
                self.get_address()
                self.get_works()
                self.get_staffs()
                self.get_contacts()
                flag = True
        else:
            self.get_conclusion_resume()
            self.get_conclusion_passport()
            self.get_conclusion_staff()
            flag - False
        self.book.close()
        return flag
        
    def get_resume(self):
        # основные данные
        Forms.resume = dict(full_name=str(self.sheet['K3'].value).title().strip(),
                        last_name=str(self.sheet['S3'].value).title().strip(),
                        birthday=datetime.strftime(datetime.strptime(str(self.sheet['L3'].value).strip(),
                                                                     '%d.%m.%Y'), '%Y-%m-%d'),
                        birth_place=str(self.sheet['M3'].value).strip(),
                        country=str(self.sheet['T3'].value).strip(),
                        snils=str(self.sheet['U3'].value).strip(),
                        inn=str(self.sheet['V3'].value).strip(),
                        education=str(self.sheet['X3'].value).strip())
        return Forms.resume
                        
    def get_passport(self):
        Forms.passports = [dict(series_passport=str(self.sheet['P3 '].value).strip(),
                        number_passport=str(self.sheet['Q3 '].value).strip(),
                        date_given=datetime.strftime(datetime.strptime(str(self.sheet['R3 '].value).strip(),
                                                                       '%d.%m.%Y'), '%Y-%m-%d'))]
        return Forms.passports
                                                                       
    def get_address(self):
        Forms.address = [dict(type = 'Адрес регистрации', address=str(self.sheet['N3'].value).strip()), 
                        dict(type = 'Адрес проживания', address=str(self.sheet['O3'].value).strip())]
        return Forms.address

    def get_contacts(self):
        Forms.contacts = [dict(type = 'Телефон', contact=str(self.sheet['Y3 '].value).strip()),
                   dict(type = 'e-mail', contact=str(self.sheet['Z3'].value).strip())]
        return Forms.contacts

    def get_works(self):
        Forms.works = [dict(period=str(self.sheet['AA3'].value).strip(), workplace=str(self.sheet['AB3'].value).strip(),
                        address=str(self.sheet['AC3'].value).strip(), staff=self.sheet['AD3'].value.strip()),
                   dict(period=str(self.sheet['AA4'].value).strip(), workplace=str(self.sheet['AB4'].value).strip(),
                        address=str(self.sheet['AC4'].value).strip(), staff=self.sheet['AD4'].value.strip()),
                   dict(period=str(self.sheet['AA5'].value).strip(), workplace=str(self.sheet['AB5'].value).strip(),
                        address=str(self.sheet['AC5'].value).strip(), staff=self.sheet['AD5'].value.strip())]
        return Forms.works

    def get_staffs(self):
        Forms.staffs = [dict(staff=str(self.sheet['C3'].value).strip(), department=str(self.sheet['D3'].value).strip(),
                        recruiter=str(self.sheet['E3'].value).strip())]
        return Forms.staffs

    def get_last_names(self):
        Forms.last_names = [dict(last_name=str(self.sheet['S3'].value).strip)]
        self.wb.close() 
        return Forms.last_names

    def excel_full_data(result):  # загрузка данных из Excel файла в БД кроме основных данных
        for name in Forms.last_names:
            if name['last_name'] is not None:
                name['last_name_id'] = result.id
                session.add(LastName(**name))  
                session.commit()
        for passport in Forms.passports:
            if passport['number_passport'] is not None:
                passport['passport_id'] = result.id
                session.add(Passport(**passport))  
                session.commit()
        for addr in Forms.addresses:
            if addr['address'] is not None:
                addr['address_id'] = result.id
                session.add(Address(**addr))  
                session.commit()
        for cont in Forms.contacts:
            if cont['contact'] is not None:
                cont['phone_id'] = result.id
                session.add(Contact(**cont))  
                session.commit()
        for place in Forms.works:
            if place['workplace'] is not None:
                place['work_place_id'] = result.id
                session.add(Workplace(**place))  
                session.commit()
        for staff in Forms.staffs:
            if staff['staff'] is not None:
                staff['staff_id'] = result.id
                session.add(Staff(**staff))  
                session.commit()

    def get_conclusion_resume(self):
        Forms.resumes = {'full_name': self.sheet['C6'].value,
                        'birthday': self.sheet['C8'].value}
        return Forms.resumes

    def get_conclusion_passport(self):
        Forms.passports = [{'series_passport': self.sheet['C9'].value,
                        'number_passport': self.sheet['D9'].value,
                        'date_given': self.sheet['E9'].value}]
        return Forms.passports
    
    def get_conclusion_staff(self):
        Forms.staffs = [{'staff': self.sheet['C4'].value,
                        'department': self.sheet['C5'].value}]
        return Forms.staffs

    def excel_short_data(result):
        Forms.resume['last_name_id'] = result.id
        session.add(LastName(**Forms.resume))  
        session.commit()
        for passport in Forms.passports:
            if passport['number_passport'] is not None:
                passport['passport_id'] = result.id
                session.add(Passport(**passport))  
                session.commit()
        for staff in Forms.staffs:
            if staff['number_passport'] is not None:
                staff['passport_id'] = result.id
                session.add(Passport(**staff))  
                session.commit()

    def get_check(self):
        Forms.checks = {'check_work_place':
                            f"{self.sheet['C11'].value} - {self.sheet['D11'].value}; {self.sheet['C12'].value} - "
                            f"{self.sheet['D12'].value}; {self.sheet['C13'].value} - {self.sheet['D13'].value}",
                        'check_cronos':
                            f"{self.sheet['B14'].value}: {self.sheet['C14'].value}; {self.sheet['B15'].value}: "
                            f"{self.sheet['C15'].value}",
                        'check_cross': self.sheet['C16'].value,
                        'check_passport': self.sheet['C17'].value,
                        'check_debt': self.sheet['C18'].value,
                        'check_bankruptcy': self.sheet['C19'].value,
                        'check_bki': self.sheet['C20'].value,
                        'check_affiliation': self.sheet['C21'].value,
                        'check_internet': self.sheet['C22'].value,
                        'resume': self.sheet['C23'].value,
                        'date_check': datetime.strftime(datetime.strptime(str(self.sheet['C24'].value).\
                            strip(), '%d.%m.%Y'), '%Y-%m-%d'),
                        'officer': self.sheet['C25'].value}
        return Forms.checks


class Registries:
    """Class for registry and inquiry dates"""

    def __init__(self, sheet, num):
        self.sheet = sheet
        self.num = num
        self.chart = None
        self.inquiry = None
        self.url = None

    def get_registry(self):
        self.chart = {'marks': self.sheet[f'E{self.num}'].value,
                         'decision': self.sheet[f'J{self.num}'].value,
                         'dec_date': datetime.strftime(datetime.strptime(str(self.sheet[f'K{self.num}'].value).\
                             strip(), '%d.%m.%Y'), '%Y-%m-%d')}
        return self.chart
    
    def get_url(self):
        self.url = {'url':  self.sheet[f'L{self.num}'].value}
        return self.url
    
    def get_inquiry(self):
        self.chart = {'info': self.sheet[f'E{self.num}'].value,
                        'initiator': self.sheet[f'F{self.num}'].value,
                        'date_inq': datetime.strftime(datetime.strptime(str(self.sheet[f'G{self.num}'].value).\
                             strip(), '%d.%m.%Y'), '%Y-%m-%d')}
        return self.chart
