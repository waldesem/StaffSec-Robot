package main

import (
	"fmt"
	"os"
	"path/filepath"
	"time"
)

import (
    "github.com/xuri/excelize/v2"
    "github.com/mattn/go-sqlite3"
)

var basePath string = filepath.Join(currentPath(), "..")
var workDir string = filepath.Join(basePath, "Кандидаты")
var archiveDir string = filepath.Join(basePath, "Персонал")
var archiveDir2 string = filepath.Join(archiveDir, "Персонал-2")
var workFile string = "Кандидаты.xlsm"
var workPath string = filepath.Join(workDir, workFile)
var infoFile string = "Запросы по работникам.xlsx"
var infoPath string = filepath.Join(workDir, infoFile)
var database string = "personal.db"
var databaseURI string = "sqlite:///" + filepath.Join(basePath, database)

func currentPath() (cur string) {
	cur, err := os.Getwd()
	if err != nil {
		fmt.Println(err)
	}
	return
}

func main() {
	workFileStat, err := os.Stat(workPath)
	if err != nil {
		fmt.Println(err)
	}
	infoFileStat, err := os.Stat(infoPath)
	if err != nil {
		fmt.Println(err)
	}

	workFileDate := workFileStat.ModTime()
	infoFileDate := infoFileStat.ModTime().Unix()
    
	if time.Now().Truncate(24 * time.Hour).Equal(workFileDate) || time.Now().Truncate(24 * time.Hour).Equal(infoFileDate) {
		os.Rename(databaseURI, filepath.Join(archiveDir, database))
	}
	if time.Now().Truncate(24 * time.Hour).Equal(infoFileDate) {
		os.Rename(infoPath, filepath.Join(archiveDir, infoFile))
		parseMainFile()
	}
	if time.Now().Truncate(24 * time.Hour).Equal(workFileDate) {
		os.Rename(workPath, filepath.Join(archiveDir, workFile))
		parseInfoFile()
	}
}

func getRows(col []int) []int {
    var rowNum []int
    for _, cell := range col {
        for _, c := range cell {
            if c == nil {
                continue
            } else if c.(*excelize.Cell).Type == time.Time || c.Truncate(24*time.Hour) == time.Now().Truncate(24*time.Hour) {
                rowNum = append(rowNum, c.row)
            }
        }
    }
    return rowNum
}

func parseInfoFile() {
    f, err := excelize.OpenFile(infoFile)
    if err != nil {
        fmt.Println(err)
        return
    }
    defer func() {
        if err := f.Close(); err != nil {
            fmt.Println(err)
        }
    }()
    ws, err := f.GetwsInfo("Лист1")
    if err != nil {
        fmt.Println(err)
        return
    }
    numRow := getRows(ws["G"])
    if len(numRow) == 0 {
        return
    }
    for _, num := range numRow {
        chart := map[string]interface{}{
            "info": ws["E" + str(num)].value,
            "initiator": ws["F" + str(num)].value,
            "fullname": ws["A" + str(num)].value,
            "deadline": time.Now().Truncate(24 * time.Hour),
            "birthday": ws["B" + str(num)].Truncate(24 * time.Hour
            }
        db, err := sqlite3.Open(databaseURI)
        if err != nil {
            fmt.Println(err)
            return
        }
        defer func() {
            if err := db.Close(); err != nil {
                fmt.Println(err)
            }
        }
        rows, err := db.Query("SELECT * FROM persons WHERE fullname = ? AND birthday = ?",
                (chart["fullname"], chart["birthday"])
            )
        if err != nil {
            fmt.Println(err)
            return
        }
        
        if not result:
            cursor.execute("INSERT INTO persons (fullname, birthday, create, category_id, region_id, status_id) \
                            VALUES (?, ?)", (chart["fullname"], chart["birthday"],
                                            chart["deadline"]), 1, 1, 9)
        else:
            cursor.execute("UPDATE persons SET update = ? WHERE id = ?",
                        date.today(), result[0])
        cursor.execute("INSERT INTO inquiries (info, initiator, deadline, person_id) \
                        VALUES (?, ?, ?, ?)",
                        (chart["info"], chart["initiator"], date.today(), result[0]))
        conn.commit()
    }
    wb.close()
}    

func parseMainFile() {
	wb := excelize.OpenFile(mainFile)
}


def parseMainFile():
    wb = load_workbook(Config.MAIN_FILE, keep_vba=True, read_only=False)
    ws = wb.workwss[0]
    num_row = range_row(ws["K"])

    if len(num_row):
        # list of directories with candidates names
        fio = [ws["B" + str(i)].value.strip().lower() for i in num_row]
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
                    if str(ws["B" + str(n)].value.strip().lower()) == sub.strip().lower():
                        sbd = ws["B" + str(n)].value.strip()
                        lnk = os.path.join(Config.ARCHIVE_DIR_2, sbd[0][0], f"{sbd} - {ws["A" + str(n)].value}")
                        ws["L" + str(n)].hyperlink = str(lnk)  # записывает в книгу
                        shutil.move(os.path.join(Config.WORK_DIR, sbd), lnk)

             screenRegistryData(ws, num_row)
        wb.save(Config.MAIN_FILE)
    else:
        wb.close()

def screenRegistryData(ws, num_row):
    for num in num_row:
        chart = {"fullname": ws["A" + str(num)].value,
                 "birthday": (ws["B" + str(num)].value).date() \
                    if isinstance(ws["B" + str(num)].value, datetime)
                        else date.today(),
                 "decision": ws[f"J{num}"].value,
                 "deadline": date.today(),
                 "url": ws[f"L{num}"].value}
        connection = sqlite3.connect(Config.DATABASE_URI)
        with connection as conn:
            cursor = conn.cursor()
            person = cursor.execute(
                "SELECT * FROM persons WHERE fullname = ? AND birthday = ?",
                (chart["fullname"], chart["birthday"])
            )
            result = person.fetchone()
            if not result:
                cursor.execute("INSERT INTO persons (fullname, birthday, path)",
                               (chart["fullname"], chart["birthday"], chart["url"]))

                cursor.execute(f"UPDATE checks SET conclusion_id = ?, deadline = ?, person_id = ?)",
                               (get_conclusion_id(chart["decision"]),
                                chart["deadline"], cursor.lastrowid))
            else:
                cursor.execute("UPDATE persons SET path = ? WHERE id = ?",
                               (chart["url"], result[0]))
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
