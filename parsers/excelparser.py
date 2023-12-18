from datetime import datetime
import openpyxl

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.model import Person, Status, Category, Check, Robot, engine
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
            else:
                self.person.append(dict(resume = self.get_conclusion_resume(worksheet)))
            self.person.append(dict(check = self.get_check(worksheet)))
        else:
            self.person.append(dict(robot = self.get_robot(worksheet)))
            self.person.append(dict(robot = self.get_robot(worksheet)))

        workbook.close()

    @staticmethod
    def get_resume(sheet):
        resume = dict(fullname=str(sheet['K3'].value).title().strip(),
                        birthday=datetime.strftime(
                            datetime.strptime(str(sheet['L3'].value).strip(), 
                                              '%d.%m.%Y'), '%Y-%m-%d'
                                              ),
                        birthplace=str(sheet['M3'].value).strip(),
                        country=str(sheet['T3'].value).strip(),
                        snils=str(sheet['U3'].value).strip(),
                        inn=str(sheet['V3'].value).strip())
        return resume

    @staticmethod
    def get_conclusion_resume(sheet):
        resumes = {'fullname': sheet['C6'].value,
                    'birthday': sheet['C8'].value}
        return resumes
    
    @staticmethod
    def get_robot_resume(sheet):
        resumes = {'fullname': sheet['B4'].value,
                    'birthday': datetime.strftime(
                        datetime.strptime(str(sheet['B5'].value).strip(), 
                                          '%d.%m.%Y'), '%Y-%m-%d'
                                          )}
        return resumes

    @staticmethod
    def get_check(sheet):
        checks = {
            'workplace': f"{sheet['C11'].value} - {sheet['D11'].value}; {sheet['C12'].value} - "
                         f"{sheet['D12'].value}; {sheet['C13'].value} - {sheet['D13'].value}",
            'cronos': f"{sheet['B14'].value}: {sheet['C14'].value}; {sheet['B15'].value}: "
                      f"{sheet['C15'].value}",
            'cros': sheet['C16'].value,
            'document': sheet['C17'].value,
            'debt': sheet['C18'].value,
            'bankruptcy': sheet['C19'].value,
            'bki': sheet['C20'].value,
            'affiliation': sheet['C21'].value,
            'internet': sheet['C22'].value,
            'pfo': True if sheet['C2^'].value in ['Назначено', 
                                                  'На испытательном сроке'] else False,
            'addition': sheet['C28'].value,
            'conclusion': sheet['C23'].value,
            'officer': sheet['C25'].value}
        return checks

    @staticmethod
    def get_robot(sheet):
        robot = {
            'employee': sheet['B27'].value,
            'terrorist': sheet['B17'].value,
            'inn': sheet['B18'].value,
            'bankruptcy': f"{sheet['B20'].value}, {sheet['B21'].value}, {sheet['B22'].value}",
            'mvd': sheet['B23'].value,
            'courts': sheet['B24'].value,
            'bki': sheet['B25'].value,
            }
        return robot
