import sqlite3

CONNECT_OLD = r'\\cronosx1\New folder\УВБ\Отдел корпоративной защиты\\personal — копия.db'
CONNECT_NEW = r'\\cronosx1\New folder\УВБ\\personal_new.db'


def response(db, query):
    with sqlite3.connect(db) as con:
        cur = con.cursor()
        cur.execute(query)
        record_db = cur.fetchall()
        con.commit()
        return record_db

def insert(db, query, value):
    with sqlite3.connect(db) as con:
        cur = con.cursor()
        cur.executemany(query, value)
        con.commit()


if __name__ == "__main__":
    # переносим данные из таблицы кандидатов в новую таблицу кандидатов по столбцам
    insert(CONNECT_NEW, f'INSERT INTO candidates (full_name, birthday, birth_place, country, snils, inn, education) \
        VALUES ({"?, "*(6)} ?)', response(CONNECT_OLD, 'SELECT full_name,  birthday,  birth_place,  country,  snils,  \
            inn,  education from candidates'))
    response(CONNECT_NEW, "update candidates set STATUS='Закончен' WHERE id is not NULL")

    # переносим данные из таблицы кандидатов в таблицу last_name по столбцам
    insert(CONNECT_NEW, f'INSERT INTO last_names (last_name, last_name_id) \
        VALUES (?, ?)', response(CONNECT_OLD, 'SELECT last_name, id from candidates \
            WHERE last_name is not NULL or last_name <> "None"'))
            
    # переносим данные из таблицы кандидатов в таблицу passports по столбцам
    insert(CONNECT_NEW, f'INSERT INTO passports (series_passport, number_passport, date_given, passport_id) \
        VALUES ({"?, "*(3)} ?)', response(CONNECT_OLD, 'SELECT series_passport, number_passport, date_given, id \
            from candidates WHERE number_passport is not NULL or number_passport <> "None"'))

    # переносим данные из таблицы кандидатов в таблицу addresses по совпадающим столбцам
    insert(CONNECT_NEW, f'INSERT INTO addresses (address, address_id) \
        VALUES (?, ?)', response(CONNECT_OLD, 'SELECT reg_address, id from candidates \
            WHERE reg_address is not NULL or reg_address <> "None"'))
    response(CONNECT_NEW, "update addresses set type='Адрес регистрации' WHERE address is not NULL or address <> 'None'")

    # переносим данные из таблицы кандидатов в таблицу addresses по столбцам
    insert(CONNECT_NEW, f'INSERT INTO addresses (address, address_id) \
        VALUES (?, ?)', response(CONNECT_OLD, 'SELECT live_address, id from candidates \
            WHERE live_address is not NULL or live_address <> "None"'))
    response(CONNECT_NEW, "update addresses set type='Адрес проживания' WHERE type is NULL \
        and(address is not NULL or address <> 'None')")

    # переносим данные из таблицы кандидатов в таблицу contacts по столбцам
    insert(CONNECT_NEW, f'INSERT INTO contacts (contact, contact_id) \
        VALUES (?, ?)', response(CONNECT_OLD, 'SELECT phone, id from candidates \
            WHERE phone is not NULL or phone <> "None"'))
    response(CONNECT_NEW, "update contacts set type='Мобильный номер' \
        WHERE contact is not NULL or contact <> 'None'")

    # переносим данные из таблицы кандидатов в таблицу contacts по столбцам
    insert(CONNECT_NEW, f'INSERT INTO contacts (contact, contact_id) \
        VALUES (?, ?)', response(CONNECT_OLD, 'SELECT email, id from candidates \
            WHERE email is not NULL or email <> "None"'))
    response(CONNECT_NEW, "update contacts set type='e-mail' WHERE type is NULL \
        and(contact is not NULL or contact <> 'None')")

    # переносим данные из таблицы кандидатов в таблицу staffs по столбцам
    insert(CONNECT_NEW, f'INSERT INTO staffs (staff, department, staff_id) \
        VALUES (?, ?, ?)', response(CONNECT_OLD, 'SELECT staff, department, id from candidates \
            WHERE staff is not NULL or staff <> "None"'))

    # переносим данные из таблицы checks в таблицу checks по столбцам
    insert(CONNECT_NEW, f'INSERT INTO checks (check_work_place, check_passport, check_debt, \
            check_bankruptcy, check_bki, check_affiliation, check_internet, check_cronos, check_cross, resume, \
                date_check, officer, check_id) VALUES ({"?, "*(12)} ?)', \
                    response(CONNECT_OLD, 'SELECT check_work_place, check_passport, check_debt, \
            check_bankruptcy, check_bki, check_affiliation, check_internet, check_cronos, check_cross, resume, \
                date_check, officer, check_id from checks WHERE resume is not NULL or resume <> "None"'))

    # переносим данные из таблицы inqueries в таблицу inqueries по столбцам
    insert(CONNECT_NEW, f'INSERT INTO inqueries (info, initiator, date_inq, iquery_id) VALUES (?, ?, ?, ?)', \
                    response(CONNECT_OLD, 'SELECT info, firm, date_inq, iquery_id from iqueries \
                        WHERE info is not NULL or info <> "None"'))   

    # переносим данные из таблицы registries в таблицу registries по столбцам
    insert(CONNECT_NEW, f'INSERT INTO registries (marks, decision, dec_date, registry_cand_id) VALUES (?, ?, ?, ?)', \
                    response(CONNECT_OLD, 'SELECT checks, fin_decision, final_date, registry_id from registries \
                        WHERE fin_decision is not NULL or fin_decision <> "None"'))   

    # переносим данные из таблицы registries в таблицу checks по столбцам
    registries = response(CONNECT_OLD, 'SELECT url, registry_id from registries WHERE \
        fin_decision is not NULL or fin_decision <> "None"')
    for i in range(len(registries)):
        value = (registries[i][-2], registries[i][-1])
        print(value)
        response(CONNECT_NEW, f'update checks set url = ? WHERE check_id = ?', value)