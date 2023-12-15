import re
import json
from datetime import datetime

from ..models.model import Region, Status, Category
from ..models.classes import Statuses, Categories


class JsonFile:
    """ Create class for import data from json file"""

    def __init__(self, file) -> None:
        with open(file, 'r', newline='', encoding='utf-8-sig') as f:
            self.json_dict = json.load(f)

            self.resume = {
                'region_id': self.parse_region(),
                'category_id': Category().get_id(Categories.candidate.name),
                'status_id': Status().get_id(Statuses.new.name),
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
    
    def parse_region(self):
        if 'department' in self.json_dict:
            divisions = re.split(r'/', self.json_dict['department'].strip())
            for div in divisions:
                region_id = Region().get_id(div)
                if region_id:
                    return region_id
                else:
                    return 1
    
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