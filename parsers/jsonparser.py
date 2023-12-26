import json
import sqlite3
from datetime import datetime

from config import Config


def json_to_db(json_path):
    for json_file in json_path:
        json_data = JsonFile(json_file)
        connection = sqlite3.connect(Config.DATABASE_URI)
        with connection as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM persons WHERE fullname = ? AND birthday = ?",
                (json_data.resume['fullname'], json_data.resume['birthday'])
            )
            result = cursor.fetchone()
            person_id = result[0] if result else None
        
            if person_id:
                cursor.execute(
                    f"UPDATE persons SET {','.join(json_data.resume['resume'].keys())} "
                    f"WHERE id = {person_id}",
                    tuple(json_data.resume['resume'].values())
                )
            else:
                cursor.execute(
                    f"INSERT INTO persons ({','.join(json_data.resume['resume'].keys())}) "
                    f"VALUES ({','.join(['?'] * len(json_data.resume['resume'].values()))})", 
                    tuple(json_data.resume['resume'].values())
                )
                person_id = cursor.lastrowid
            
            models = ['staffs', 'documents', 'addresses', 'contacts', 'workplaces', 'affilations']
            items_lists = [json_data.staff, json_data.passport, json_data.addresses, 
                            json_data.contacts, json_data.workplaces, json_data.affilation]
            
            for model, items in zip(models, items_lists):
                for item in items:
                    if item:
                        cursor.execute(
                            f"INSERT INTO {model} ({','.join(item.keys())}, person_id) ",
                            tuple(item.values()) + (person_id,)
                        )
            conn.commit()


class JsonFile:
    """ Create class for import data from json file"""

    def __init__(self, file) -> None:
        with open(file, 'r', newline='', encoding='utf-8-sig') as f:
            self.json_dict = json.load(f)

            self.resume = {
                'region_id': self.parse_region(),
                'category_id': self.get_category_id("Кандидат"),
                'status_id': self.get_status_id("Окончено"),
                'fullname': self.parse_fullname(),
                'previous': self.parse_previous(),
                'birthday': self.parse_birthday(),
                'birthplace': self.json_dict.get('birthplace', '').strip(),
                'country': self.json_dict.get('citizen' '').strip(),
                'ext_country': self.json_dict.get('additionalCitizenship', '').strip(),
                'snils': self.json_dict.get('snils', '').strip(),
                'inn': self.json_dict.get('inn', '').strip(),
                'marital': self.json_dict.get('maritalStatus', '').strip(),
                'education': self.parse_education()
            }
            
            self.workplaces = self.parse_workplace()
            
            self.passport = [
                {
                    'view': 'Паспорт',
                    'series': self.json_dict.get('passportSerial', '').strip(),
                    'number': self.json_dict.get('passportNumber', '').strip(),
                    'issue': datetime.strptime(
                        self.json_dict.get('passportIssueDate', '1900-01-01'), '%Y-%m-%d'
                        ),
                    'agency': self.json_dict.get('passportIssuedBy', '').strip(),
                }
            ]
            self.addresses = [
                {
                    'view': "Адрес регистрации", 
                    'address': self.json_dict.get('regAddress', '').strip(),
                },
                {
                    'view': "Адрес проживания", 
                    'address': self.json_dict.get('validAddress', '').strip(),
                }
            ]
            self.contacts = [
                {
                    'view': 'Мобильный телефон', 
                    'contact': self.json_dict.get('contactPhone', '').strip(),
                },
                {
                    'view': 'Электронная почта', 
                    'contact': self.json_dict.get('email', '').strip(),
                }
            ]
            self.staff = [
                {
                    'position': self.json_dict.get('positionName', '').strip(),
                    'department': self.json_dict.get('department', '').strip()
                }
            ]
            self.affilation = self.parse_affilation()
    
    def get_category_id(self, name):
        connection = sqlite3.connect(Config.DATABASE_URI)
        with connection as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM categories WHERE category = ?",
                (name, )
            )
            result = cursor.fetchone()
            return result[0] if result else 1
    
    def get_status_id(self, name):
        connection = sqlite3.connect(Config.DATABASE_URI)
        with connection as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM statuses WHERE status = ?",
                (name, )
            )
            result = cursor.fetchone()
            return result[0] if result else 1
        
    def get_region_id(self, name):
        connection = sqlite3.connect(Config.DATABASE_URI)
        with connection as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM regions WHERE region = ?",
                (name, )
            )
            result = cursor.fetchone()
            return result[0]

    def parse_region(self):
        if 'department' in self.json_dict:
            region_id = 1
            divisions = self.json_dict['department'].split('/')
            for div in divisions:
                region = self.get_region_id(div)
                if region:
                    region_id = region
            return region_id

    def parse_fullname(self):
        lastName = self.json_dict.get('lastName').strip()
        firstName = self.json_dict.get('firstName').strip()
        midName = self.json_dict.get('midName', '').strip()
        return f"{lastName} {firstName} {midName}".rstrip()
    
    def parse_birthday(self):
        birthday = datetime.strptime(self.json_dict.get('birthday', '1900-01-01'), '%Y-%m-%d')
        return birthday

    def parse_previous(self):
        if 'hasNameChanged' in self.json_dict:
            if len(self.json_dict['nameWasChanged']):
                previous = []
                for item in self.json_dict['nameWasChanged']:
                    firstNameBeforeChange = item.get('firstNameBeforeChange', '').strip()
                    lastNameBeforeChange = item.get('lastNameBeforeChange', '').strip()
                    midNameBeforeChange = item.get('midNameBeforeChange', '').strip()
                    yearOfChange = str(item.get('yearOfChange', '')).strip()
                    reason = str(item.get('reason', '')).strip()
                    previous.append(f"{yearOfChange} - {firstNameBeforeChange} "
                                    f"{lastNameBeforeChange} {midNameBeforeChange}, "
                                    f"{reason}".replace("  ", ""))
                return '; '.join(previous)
        return ''
    
    def parse_education(self):
        if 'education' in self.json_dict:
            if len(self.json_dict['education']):
                education = []
                for item in self.json_dict['education']:
                    institutionName = item.get('institutionName').strip()
                    endYear = item.get('endYear', 'н.в.')
                    specialty = item.get('specialty').strip()
                    education.append(f"{str(endYear)} - {institutionName}, "
                                     f"{specialty}".replace("  ", ""))
                return '; '.join(education)
        return ''
    
    def parse_workplace(self):
        if 'experience' in self.json_dict:
            if len(self.json_dict['experience']):
                experience = []
                for item in self.json_dict['experience']:
                    work = {
                        'start_date': datetime.strptime(item.get('beginDate', '1900-01-01'), '%Y-%m-%d'),
                        'end_date': datetime.strptime(item['endDate'], '%Y-%m-%d') \
                            if 'endDate' in item else datetime.now(),
                        'workplace': item.get('name', '').strip(),
                        'address': item.get('address', '').strip(),
                        'position': item.get('position', '').strip(),
                        'reason': item.get('fireReason', '').strip()
                    }
                    experience.append(work)
                return experience
        return []
    
    def parse_affilation(self):
        affilation = []
        if self.json_dict['hasPublicOfficeOrganizations']:
            if len(self.json_dict['publicOfficeOrganizations']):
                for item in self.json_dict['publicOfficeOrganizations']:
                    public = {
                        'view': 'Являлся государственным или муниципальным служащим',
                        'name': f"{item.get('name', '')}",
                        'position': f"{item.get('position', '')}"
                    }
                    affilation.append(public)

        if self.json_dict['hasStateOrganizations']:
            if len(self.json_dict['stateOrganizations']):
                for item in self.json_dict['publicOfficeOrganizations']:
                    state = {
                        'view': 'Являлся государственным должностным лицом',
                        'name': f"{item.get('name', '')}",
                        'position': f"{item.get('position', '')}"
                    }
                    affilation.append(state)

        if self.json_dict['hasRelatedPersonsOrganizations']:
            if len(self.json_dict['relatedPersonsOrganizations']):
                for item in self.json_dict['relatedPersonsOrganizations']:
                    related = {
                        'view': 'Связанные лица работают в госудраственных организациях',
                        'name': f"{item.get('name', '')}",
                        'position': f"{item.get('position', '')}",
                        'inn': f"{item.get('inn'), ''}"
                    }
                    affilation.append(related)
        
        if self.json_dict['hasOrganizations']:
            if len(self.json_dict['organizations']):
                for item in self.json_dict['organizations']:
                    organization = {
                        'view': 'Участвует в деятельности коммерческих организаций"',
                        'name': f"{item.get('name', '')}",
                        'position': f"{item.get('workCombinationTime', '')}",
                        'inn': f"{item.get('inn'), ''}"
                    }
                    affilation.append(organization)
        return affilation