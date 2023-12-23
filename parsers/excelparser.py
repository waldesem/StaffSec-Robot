from datetime import datetime
import sqlite3
import openpyxl

from config import Config


def excel_to_db(path_files):  # take path's to conclusions
    for path in path_files:
        excel = ExcelFile(path)
        excel.person['resume'].update({
            'category_id': 1,
            'status_id': 9,
            'region_id': 1
            })
        connection = sqlite3.connect(Config.DATABASE_URI)
        with connection as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM persons WHERE fullname = ? AND birthday = ?",
                (excel.person['resume']['fullname'], excel.person['resume']['birthday'])
            )
            result = cursor.fetchone()
            person_id = result[0] if result else None

            if not person_id:
                cursor.execute(
                    f"INSERT INTO persons ({','.join(excel.person['resume'].keys())}) "
                    f"VALUES ({','.join(['?'] * len(excel.person['resume'].values()))})", 
                    tuple(excel.person['resume'].values())
                )
                conn.commit()
                person_id = cursor.lastrowid
            else:
                cursor.execute(
                    f"UPDATE persons SET {','.join(excel.person['resume'].keys())} "
                    f"WHERE id = {person_id}",
                    tuple(excel.person['resume'].values())
                )
                conn.commit()

            if excel.person['check']:
                cursor.execute(
                    f"INSERT INTO checks ({','.join(excel.person['check'].keys())}, person_id) ",
                    tuple(excel.person['check'].values()) + (person_id,)
                )
                conn.commit()
            elif excel.person['robot']:
                cursor.execute(
                    f"INSERT INTO robots ({','.join(excel.person['robot'].keys())}, person_id) ",
                    tuple(excel.person['robot'].values()) + (person_id,)
                )
                conn.commit()


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
            'conclusion': ExcelFile.get_conclusion_id(sheet['C23'].value),
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

    @staticmethod
    def get_conclusion_id(name):
        connection = sqlite3.connect(Config.DATABASE_URI)
        with connection as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM conclusions WHERE conclusion = ?",
                (name, )
            )
            result = cursor.fetchone()
        return result