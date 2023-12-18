from datetime import datetime
import openpyxl

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.model import Person, Status, Category, Staff, Document, \
    Address, Contact, Workplace, Check, Robot, engine
from ..models.classes import Categories, Statuses


def excel_to_db(path_files):  # take path's to conclusions
    for path in path_files:
        excel = ExcelFile(path)
        excel.person['resume'].update({
            'category_id': Category().get_id(Categories.candidate.value),
            'status_id': Status().get_id(Statuses.finish.value),
            'region_id': 1
            })
        
        with Session(engine) as sess:  # get personal dates
            result = sess.execute(
                select(Person)
                .filter_by(fullname=excel.person['resume']['fullname'], 
                           birthday=excel.person['resume']['birthday'])
                ).scalar_one_or_none()
            person_id = result.id

            if not result:
                resume = Person(**excel.person['resume'])
                sess.add(resume)
                sess.flush()
                person_id = resume.id
            else:
                for k, v in excel.person['resume'].items():
                    if v:
                        setattr(result, k, v)

            if excel.person['check']:
                    sess.add(Check(**excel.person['check'] | {'person_id': person_id}))
            elif excel.person['robot']:
                sess.add(Robot(**excel.person['robot'] | {'person_id': person_id}))

            models = [Staff, Document, Address, Contact, Workplace]
            items_lists = [excel.person['staff'], excel.person['passport'], 
                           excel.person['addresses'], excel.person['contacts'], 
                           excel.person['workplaces']]
            for model, items in zip(models, items_lists):
                for item in items:
                    if item:
                        sess.add(model(**item | {'person_id': person_id}))

            sess.commit()


class ExcelFile:
    
    def __init__(self, path):
        self.person = []
        self.screen_excel(path)
        
    def screen_excel(self, path):
        workbook = openpyxl.load_workbook(path, keep_vba=True)
        worksheet = workbook.worksheets[0]
        if path.startswith("Заключение"):
            if len(workbook.sheetnames) > 1:
                sheet = workbook.worksheets[1]
                if str(sheet['K1'].value) == 'ФИО':
                    self.person.append(dict(resume = self.get_resume(sheet)))
                    self.person.append(dict(passport = self.get_passport(sheet)))
                    self.person.append(dict(staff = self.get_staffs(sheet)))
                    self.person.append(dict(works = self.get_works(sheet)))
                    self.person.append(dict(address = self.get_address(sheet)))
                    self.person.append(dict(contacts = self.get_contacts(sheet)))
            else:
                self.person.append(dict(resume = self.get_conclusion_resume(worksheet)))
                self.person.append(dict(passport = self.get_conclusion_passport(worksheet)))
                self.person.append(dict(staff = self.get_conclusion_staff(worksheet)))
                self.person.append(dict(check = self.get_check(worksheet)))
        else:
            self.person.append(dict(robot = self.get_robot(worksheet)))

        workbook.close()

    @staticmethod
    def get_resume(sheet):
        resume = dict(full_name=str(sheet['K3'].value).title().strip(),
                        last_name=str(sheet['S3'].value).title().strip(),
                        birthday=datetime.strftime(datetime.strptime(str(sheet['L3'].value).strip(),
                                                                        '%d.%m.%Y'), '%Y-%m-%d'),
                        birth_place=str(sheet['M3'].value).strip(),
                        country=str(sheet['T3'].value).strip(),
                        snils=str(sheet['U3'].value).strip(),
                        inn=str(sheet['V3'].value).strip(),
                        education=str(sheet['X3'].value).strip())
        return resume

    @staticmethod
    def get_passport(sheet):
        passports = [dict(series_passport=str(sheet['P3 '].value).strip(),
                        number_passport=str(sheet['Q3 '].value).strip(),
                        date_given=datetime.strftime(datetime.strptime(str(sheet['R3 '].value).strip(),
                                                                        '%d.%m.%Y'), '%Y-%m-%d'))]
        return passports

    @staticmethod
    def get_address(sheet):
        address = [dict(type = 'Адрес регистрации', address=str(sheet['N3'].value).strip()), 
                        dict(type = 'Адрес проживания', address=str(sheet['O3'].value).strip())]
        return address


    def get_contacts(sheet):
        contacts = [dict(type = 'Телефон', contact=str(sheet['Y3 '].value).strip()),
                    dict(type = 'e-mail', contact=str(sheet['Z3'].value).strip())]
        return contacts

    @staticmethod
    def get_works(sheet):
        works = [dict(period=str(sheet['AA3'].value).strip(), workplace=str(sheet['AB3'].value).strip(),
                        address=str(sheet['AC3'].value).strip(), staff=sheet['AD3'].value.strip()),
                    dict(period=str(sheet['AA4'].value).strip(), workplace=str(sheet['AB4'].value).strip(),
                        address=str(sheet['AC4'].value).strip(), staff=sheet['AD4'].value.strip()),
                    dict(period=str(sheet['AA5'].value).strip(), workplace=str(sheet['AB5'].value).strip(),
                        address=str(sheet['AC5'].value).strip(), staff=sheet['AD5'].value.strip())]
        return works

    @staticmethod
    def get_staffs(sheet):
        staffs = [dict(staff=str(sheet['C3'].value).strip(), department=str(sheet['D3'].value).strip(),
                        recruiter=str(sheet['E3'].value).strip())]
        return staffs

    @staticmethod
    def get_conclusion_resume(sheet):
        resumes = {'full_name': sheet['C6'].value,
                    'birthday': sheet['C8'].value,
                    'previous_name': sheet['C7'].value}
        return resumes

    @staticmethod
    def get_conclusion_passport(sheet):
        passports = [{'series_passport': sheet['C9'].value,
                        'number_passport': sheet['D9'].value,
                        'date_given': sheet['E9'].value}]
        return passports

    @staticmethod
    def get_conclusion_staff(sheet):
        staffs = [{'staff': sheet['C4'].value,
                        'department': sheet['C5'].value}]
        return staffs

    @staticmethod
    def get_check(sheet):
        checks = {'check_work_place':
                            f"{sheet['C11'].value} - {sheet['D11'].value}; {sheet['C12'].value} - "
                            f"{sheet['D12'].value}; {sheet['C13'].value} - {sheet['D13'].value}",
                        'check_cronos':
                            f"{sheet['B14'].value}: {sheet['C14'].value}; {sheet['B15'].value}: "
                            f"{sheet['C15'].value}",
                        'check_cross': sheet['C16'].value,
                        'check_passport': sheet['C17'].value,
                        'check_debt': sheet['C18'].value,
                        'check_bankruptcy': sheet['C19'].value,
                        'check_bki': sheet['C20'].value,
                        'check_affiliation': sheet['C21'].value,
                        'check_internet': sheet['C22'].value,
                        'resume': sheet['C23'].value,
                        'date_check': datetime.strftime(datetime.strptime(str(sheet['C24'].value).\
                            strip(), '%d.%m.%Y'), '%Y-%m-%d'),
                        'officer': sheet['C25'].value}
        return checks

    @staticmethod
    def get_robot(sheet):
        robot = {'check_work_place':
                            f"{sheet['C11'].value} - {sheet['D11'].value}; {sheet['C12'].value} - "
                            f"{sheet['D12'].value}; {sheet['C13'].value} - {sheet['D13'].value}",
                        'check_cronos':
                            f"{sheet['B14'].value}: {sheet['C14'].value}; {sheet['B15'].value}: "
                            f"{sheet['C15'].value}",
                        'check_cross': sheet['C16'].value,
                        'check_passport': sheet['C17'].value,
                        'check_debt': sheet['C18'].value,
                        'check_bankruptcy': sheet['C19'].value,
                        'check_bki': sheet['C20'].value,
                        'check_affiliation': sheet['C21'].value,
                        'check_internet': sheet['C22'].value,
                        'resume': sheet['C23'].value,
                        'date_check': datetime.strftime(datetime.strptime(str(sheet['C24'].value).\
                            strip(), '%d.%m.%Y'), '%Y-%m-%d'),
                        'officer': sheet['C25'].value}
        return robot
