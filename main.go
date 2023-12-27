package main

import (
    "fmt"
    "os"
    "path/filepath"
    "strings"
    "time"
)

import (
   "github.com/360EntSecGroup-Skylar/excelize"
)

func main () {
    mainFileDate := time.Unix(os.Stat(ConfigInstance.MainFile).ModTime().Unix(), 0)
    infoFileDate := time.Unix(os.Stat(ConfigInstance.InfoFile).ModTime().Unix(), 0)
    if time.Now().Truncate(24 * time.Hour).Equal(mainFileDate) || time.Now().Truncate(24 * time.Hour).Equal(infoFileDate) {
        os.Rename(ConfigInstance.DatabaseURI, ConfigInstance.ArchiveDir)
    }
    if time.Now().Truncate(24 * time.Hour).Equal(infoFileDate) {
        os.Rename(ConfigInstance.InfoFile, ConfigInstance.ArchiveDir)
        parseMainFile()
    }
    if time.Now().Truncate(24 * time.Hour).Equal(mainFileDate) {
        os.Rename(ConfigInstance.MainFile, ConfigInstance.ArchiveDir)
        parse_info()
    }
}

func parseMainFile () {
    wb := excelize.OpenFile(ConfigInstance.MainFile)
    ws := wb.GetSheetName(0)
    num_row := getRows(ws)
}

func getRows(ws string) []int {
    
}

def parse_main():
    wb = load_workbook(Config.MAIN_FILE, keep_vba=True, read_only=False)
    ws = wb.worksheets[0]
    num_row = range_row(ws['K'])

    if len(num_row):
        # list of directories with candidates names
        fio = [ws['B' + str(i)].value.strip().lower() for i in num_row]
        subdir = [sub for sub in os.listdir(Config.WORK_DIR) if sub.lower().strip() in fio]

        if len(subdir):
            # получаем список путей к файлам Заключений
            excel_path = []
            json_path = []

            for sub in subdir:
                subdir_path = os.path.join(Config.WORK_DIR, sub)
                for file in os.listdir(subdir_path):
                    if (file.startswith("Заключение") or file.startswith("Результаты")) \
                        and (file.endswith("xlsm") or file.endswith("xlsx")):
                        excel_path.append(os.path.join(Config.WORK_DIR, subdir_path, file))
                    elif file.endswith("json"):
                        json_path.append(os.path.join(Config.WORK_DIR, subdir_path, file))

            # parse files and send info to database            
            if len(excel_path):
                excel_to_db(excel_path)  
            if len(json_path):
                json_to_db(json_path)

            # create url and move folders to archive
            for n in num_row:
                for sub in subdir:
                    if str(ws['B' + str(n)].value.strip().lower()) == sub.strip().lower():
                        sbd = ws['B' + str(n)].value.strip()
                        lnk = os.path.join(Config.ARCHIVE_DIR_2, sbd[0][0], f"{sbd} - {ws['A' + str(n)].value}")
                        ws['L' + str(n)].hyperlink = str(lnk)  # записывает в книгу
                        shutil.move(os.path.join(Config.WORK_DIR, sbd), lnk)
                        
            screen_registry_data(ws, num_row)
        wb.save(Config.MAIN_FILE)
    else:
        wb.close()


def parse_info():
    wb = load_workbook(Config.INFO_FILE, keep_vba=True, read_only=False)
    ws = wb.worksheets[0]
    num_row = range_row(ws['G'])
    if len(num_row):
        screen_iquiry_data(ws, num_row)
    wb.close()


def range_row(sheet):
    row_num = []
    for cell in sheet:
        for c in cell:
            if c.value:
                if isinstance(c.value, datetime) and (c.value).date() == date.today():
                    row_num.append(c.row)
    return row_num

        
def screen_iquiry_data(sheet, num_row): 
    for num in num_row:
        chart = {
            'info': sheet[f'E{num}'].value,
            'initiator': sheet[f'F{num}'].value,
            'fullname': sheet[f'A{num}'].value,
            'deadline': date.today(),
            'birthday': (sheet[f'B{num}'].value).date() \
                if isinstance((sheet[f'B{num}'].value).date(), datetime) \
                    else date.today()
            }
        connection = sqlite3.connect(Config.DATABASE_URI)
        with connection as conn:
            cursor = conn.cursor()
            person = cursor.execute(
                "SELECT * FROM persons WHERE fullname = ? AND birthday = ?", 
                (chart['fullname'], chart['birthday'])
            )
            result = person.fetchone()
            if not result:
                cursor.execute("INSERT INTO persons (fullname, birthday, create, category_id, region_id, status_id) \
                                VALUES (?, ?)", (chart['fullname'], chart['birthday'],
                                                 chart['deadline']), 1, 1, 9)
            else:
                cursor.execute("UPDATE persons SET update = ? WHERE id = ?", 
                               date.today(), result[0])
            cursor.execute("INSERT INTO inquiries (info, initiator, deadline, person_id) \
                            VALUES (?, ?, ?, ?)", 
                            (chart['info'], chart['initiator'], date.today(), result[0]))
            conn.commit()


def screen_registry_data(sheet, num_row):
    for num in num_row:
        chart = {'fullname': sheet['A' + str(num)].value,
                 'birthday': (sheet['B' + str(num)].value).date() \
                    if isinstance(sheet['B' + str(num)].value, datetime)
                        else date.today(),
                 'decision': sheet[f'J{num}'].value,
                 'deadline': date.today(),
                 'url': sheet[f'L{num}'].value}
        connection = sqlite3.connect(Config.DATABASE_URI)
        with connection as conn:
            cursor = conn.cursor()
            person = cursor.execute(
                "SELECT * FROM persons WHERE fullname = ? AND birthday = ?", 
                (chart['fullname'], chart['birthday'])
            )
            result = person.fetchone()
            if not result:
                cursor.execute("INSERT INTO persons (fullname, birthday, path)", 
                               (chart['fullname'], chart['birthday'], chart['url']))

                cursor.execute(f"UPDATE checks SET conclusion_id = ?, deadline = ?, person_id = ?)", 
                               (get_conclusion_id(chart['decision']), 
                                chart['deadline'], cursor.lastrowid))
            else:
                cursor.execute("UPDATE persons SET path = ? WHERE id = ?", 
                               (chart['url'], result[0]))
            conn.commit()

def get_conclusion_id(name):
        connection = sqlite3.connect(Config.DATABASE_URI)
        with connection as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM conclusions WHERE LOWER conclusion = ?",
                (name.lower(), )
            )
            result = cursor.fetchone()
            return result[0] if result else 1
        

if __name__ == "__main__":
    main()
