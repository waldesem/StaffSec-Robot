from datetime import datetime
import openpyxl


def screen_excel(path):
    workbook = openpyxl.load_workbook(path, keep_vba=True)
    worksheet = workbook.worksheets[0]
    person = []
    if len(workbook.sheetnames) > 1:
        sheet = workbook.worksheets[1]
        if str(sheet['K1'].value) == 'ФИО':
            person.append(dict(resume = get_resume(sheet)))
            person.append(dict(passport = get_passport(sheet)))
            person.append(dict(staff = get_staffs(sheet)))
            person.append(dict(works = get_works(sheet)))
            person.append(dict(address = get_address(sheet)))
            person.append(dict(contacts = get_contacts(sheet)))
    else:
        person.append(dict(resume = get_conclusion_resume(worksheet)))
        person.append(dict(passport = get_conclusion_passport(worksheet)))
        person.append(dict(staff = get_conclusion_staff(worksheet)))
    person.append(dict(check = get_check(sheet)))
    workbook.close()
    return person


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


def get_passport(sheet):
    passports = [dict(series_passport=str(sheet['P3 '].value).strip(),
                    number_passport=str(sheet['Q3 '].value).strip(),
                    date_given=datetime.strftime(datetime.strptime(str(sheet['R3 '].value).strip(),
                                                                    '%d.%m.%Y'), '%Y-%m-%d'))]
    return passports


def get_address(sheet):
    address = [dict(type = 'Адрес регистрации', address=str(sheet['N3'].value).strip()), 
                    dict(type = 'Адрес проживания', address=str(sheet['O3'].value).strip())]
    return address


def get_contacts(sheet):
    contacts = [dict(type = 'Телефон', contact=str(sheet['Y3 '].value).strip()),
                dict(type = 'e-mail', contact=str(sheet['Z3'].value).strip())]
    return contacts


def get_works(sheet):
    works = [dict(period=str(sheet['AA3'].value).strip(), workplace=str(sheet['AB3'].value).strip(),
                    address=str(sheet['AC3'].value).strip(), staff=sheet['AD3'].value.strip()),
                dict(period=str(sheet['AA4'].value).strip(), workplace=str(sheet['AB4'].value).strip(),
                    address=str(sheet['AC4'].value).strip(), staff=sheet['AD4'].value.strip()),
                dict(period=str(sheet['AA5'].value).strip(), workplace=str(sheet['AB5'].value).strip(),
                    address=str(sheet['AC5'].value).strip(), staff=sheet['AD5'].value.strip())]
    return works


def get_staffs(sheet):
    staffs = [dict(staff=str(sheet['C3'].value).strip(), department=str(sheet['D3'].value).strip(),
                    recruiter=str(sheet['E3'].value).strip())]
    return staffs


def get_conclusion_resume(sheet):
    resumes = {'full_name': sheet['C6'].value,
                'birthday': sheet['C8'].value,
                'previous_name': sheet['C7'].value}
    return resumes


def get_conclusion_passport(sheet):
    passports = [{'series_passport': sheet['C9'].value,
                    'number_passport': sheet['D9'].value,
                    'date_given': sheet['E9'].value}]
    return passports


def get_conclusion_staff(sheet):
    staffs = [{'staff': sheet['C4'].value,
                    'department': sheet['C5'].value}]
    return staffs


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


def excel_short_data(result):
    resume['last_name_id'] = result.id
    session.add(LastName(**resume))  
    session.commit()
    for passport in passports:
        if passport['number_passport'] is not None:
            passport['passport_id'] = result.id
            session.add(Passport(**passport))  
            session.commit()
    for staff in staffs:
        if staff['number_passport'] is not None:
            staff['passport_id'] = result.id
            session.add(Passport(**staff))  
            session.commit()


def excel_full_data(result):  # загрузка данных из Excel файла в БД кроме основных данных
    for name in last_names:
        if name['last_name'] is not None:
            name['last_name_id'] = result.id
            session.add(LastName(**name))  
            session.commit()
    for passport in passports:
        if passport['number_passport'] is not None:
            passport['passport_id'] = result.id
            session.add(Passport(**passport))  
            session.commit()
    for addr in addresses:
        if addr['address'] is not None:
            addr['address_id'] = result.id
            session.add(Address(**addr))  
            session.commit()
    for cont in contacts:
        if cont['contact'] is not None:
            cont['phone_id'] = result.id
            session.add(Contact(**cont))  
            session.commit()
    for place in works:
        if place['workplace'] is not None:
            place['work_place_id'] = result.id
            session.add(Workplace(**place))  
            session.commit()
    for staff in staffs:
        if staff['staff'] is not None:
            staff['staff_id'] = result.id
            session.add(Staff(**staff))  
            session.commit()



def excel_to_db(path_files):  # take path's to conclusions
    for path in path_files:
        person = screen_excel(path) # take conclusions data
        with Session(ENGINE) as sess:  # get personal dates
            result = sess.query(Candidate).filter_by(full_name=fio, birthday=birthday).first()
            if result is None:  # if no same data in db - add personal date and checks result
                value = Candidate(**form.resumes)
                with Session(ENGINE) as sess:
                    sess.add(value)
                    sess.flush()
                    if excel_check is True:
                        form.excel_full_data(value)
                        form.checks['check_id'] = value.id
                        value = Check(**form.checks)
                        sess.add(value)
                        sess.commit()
                    else:
                        form.excel_short_data(value)
                        form.checks['check_id'] = value.id
                        value = Check(**form.checks)
                        sess.add(value)
                        sess.commit()
            else:   # if same data in db - update personal date and add other data + checks
                with Session(ENGINE) as sess:
                    search = sess.query(Candidate).get(result.id)
                    for k, v in form.resume.items():
                        if v or v != "None":
                            setattr(search, k, v)
                    if excel_check is True:
                        form.excel_full_data(result)
                        form.checks['check_id'] = result.id
                        value = Check(**form.checks)
                        sess.add(value)
                        sess.commit()
                    else:
                        form.excel_short_data(result)
                        form.checks['check_id'] = result.id
                        value = Check(**form.checks)
                        sess.add(value)
                        sess.commit()
