from datetime import date


class Parser:
    """Initialize class for parsing directories and files"""

    def __init__(self, main_file_date, info_file_date):

        if main_file_date == date.today():
            check_main = Parse(Config.MAIN_FILE, 'K5000', 'K25000')
            check_main.cand_check()
        if info_file_date == date.today():
            check_inq = Parse(Config.INFO_FILE, 'G1', 'G3000')
            check_inq.inquiry_check()
    
        self.file = file
        self.wb = openpyxl.load_workbook(self.file, keep_vba=True, read_only=False)
        self.ws = self.wb.worksheets[0]
        self.num_row = range_row(self.ws[start:end])

    def cand_check(self):  # parse registry and conclusions and send it to database
        if len(self.num_row):
            parse_conclusions(self.ws, self.num_row)
            chart_check(self.ws, self.num_row, 'registry_id', Registry)
            self.wb.save(self.file)
        else:
            self.wb.close()

    def inquiry_check(self):  # take info from iquery and send it to database
        if len(self.num_row):
            chart_check(self.ws, self.num_row, 'iquery_id', Inquery)
        self.wb.close()
