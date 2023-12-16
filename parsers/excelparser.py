def excel_to_db(path_files):  # take path's to conclusions
    for path in path_files:
        if len(path_files):
            form = Forms(path)  
            excel_check = form.check_excel() # take conclusions data
            fio, birthday = form.resumes['full_name'], form.resumes['birthday']
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

def chart_check(sheet, num_row, chart_id, chart):  # get data from registry an inquiry
    for num in num_row:
        reg = Registries(sheet, num)    
        if chart_id == 'registry_id': # get date from registry
            excel_data = reg.get_registry().items()
            fio, birthday = sheet['B' + str(num)].value, sheet['C' + str(num)].value
        else:   # get date from inquiry
            excel_data =  reg.get_inquiry().items()
            fio, birthday = sheet['A' + str(num)].value, sheet['B' + str(num)].value
        with Session(ENGINE) as sess:   # check current values
            url_datа = reg.get_url()
            if url_datа['url']:
                result = sess.query(Candidate).filter_by(full_name=fio, birthday=birthday).first()
                check = sess.query(Check).filter_by(check_id=result.id).func.max(Check.check_id).first()
                check.url = url_datа
                sess.commit()            
            if result:  # if same data id db is True, add value to Registr or Inquiry table
                excel_data[chart_id] = result.id
                value = chart(**excel_data)
                with Session(ENGINE) as sess:
                    sess.add(value)
                    sess.commit()
            else:  # if no same data, add fio and birth to Candidate table and others to Registr and Inquiry
                value = Candidate(**{'full_name': fio, 'birthday': birthday})
                with Session(ENGINE) as sess:
                    sess.add(value)
                    sess.flush()
                    excel_data[chart_id] = value.id
                    value = chart(**excel_data)
                    sess.add(value)
                    sess.commit()
        