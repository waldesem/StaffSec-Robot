package main

import (
	"fmt"
	"os"
	"path/filepath"
	"time"
    "strings"
    "database/sql"
)

import (
    "github.com/xuri/excelize/v2"
    "github.com/mattn/go-sqlite3"
)

type infoFile struct {
    id int
    info string
    initiator string
    fullname string
    birthday time.Time
    deadline time.Time
}

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

	workFileDate := workFileStat.ModTime().Truncate(24 * time.Hour)
	infoFileDate := infoFileStat.ModTime().Truncate(24 * time.Hour)
    
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

func getNums(fileName, colName  string) []int {
	f, err := excelize.OpenFile(fileName)
	if err != nil {
		fmt.Println(err)
		return nil
	}
	defer func() {
		if err := f.Close(); err != nil {
			fmt.Println(err)
		}
	}()
	totalRows, _ := f.GetRows("Лист1")
	var numRows []int
	for i := 1; i < len(totalRows); i++ {
		cell, err := f.GetCellValue("Лист1", fmt.Sprintf("%s%d", colName, i))
		if err != nil {
			fmt.Println(err)
			return nil
		}
		if cell != "" {
			t, err := time.Parse("02/01/2006", cell)
			if err != nil {
				fmt.Println(err)
				return nil
			}
			if t.Format("2006-01-02") == time.Now().Format("2006-01-02") {
				numRows = append(numRows, i)
			}
		}
	}
	return numRows
}

func parseInfoFile() {
    numRow := getNums(workPath, "G")

    if len(numRow) > 0 {
        f, err := excelize.OpenFile(mainFile)
        if err != nil {
            fmt.Println(err)
            return
        }
        defer func() {
            if err := f.Close(); err != nil {
                fmt.Println(err)
            }
        }()

        for _, num := range numRow {
            info, _ := f.GetCellValue("Лист1", fmt.Sprintf("C%d", num))
            initiator, _ := f.GetCellValue("Лист1", fmt.Sprintf("D%d", num))
            fullname, _ := f.GetCellValue("Лист1", fmt.Sprintf("A%d", num))
            birth, _ := f.GetCellValue("Лист1", fmt.Sprintf("B%d", num))
            day, _ := time.Parse("02/01/2006", birth)
            birthday := day.Local()
            deadline := time.Now().Truncate(24 * time.Hour)

            sql.Register("sqlite3_with_extensions",
                &sqlite3.SQLiteDriver{
                    Extensions: []string{
                        "sqlite3_mod_regexp",
                    },
                })

            db, err := sql.Open("sqlite3", databaseURI)
            if err != nil {
                fmt.Println(err)
                return
            }
            defer func() {
                if err := db.Close(); err != nil {
                    fmt.Println(err)
                }
            }()

            row := db.QueryRow(
                "SELECT full_name, birthday FROM candidates WHERE full_name = $1 AND birthday = $2", 
                fullname, "1980-01-14",
            )

            if err != nil {
                fmt.Println(err)
                return
            }

            cand := person{}
            err = row.Scan(&cand.id, &cand.fullname, &cand.birthday, &cand.info, &cand.initiator)
            if err != nil || err == sql.ErrNoRows {
                return
            }
            if err == sql.ErrNoRows {
                cand.id = db.Exec(
                    "INSERT INTO persons (fullname, birthday, create, category_id, region_id, status_id) VALUES ($1, $2, $3, $4, $5, $6)", 
                        cand.fullname, cand.birthday, cand.deadline, 1, 1, 9,
                            )
            } else {
                db.Exec("UPDATE persons SET update = $1 WHERE id = $2",
                    deadline, cand.id,
                )
            }
            db.Exec(
                "INSERT INTO inquiries (info, initiator, deadline, person_id) VALUES ($1, $2, $3, $4)",
                    cand.info, cand.initiator, cand.deadline, cand.id,
            )
        }
    }
}    

func parseMainFile() {
    numRow := getNums(workPath, "K")

    if len(numRow) > 0 {
        // list of directories with candidates names
        f, err := excelize.OpenFile(mainFile)
        if err != nil {
            fmt.Println(err)
            return
        }
        defer func() {
            if err := f.Close(); err != nil {
                fmt.Println(err)
            }
        }()

        var fio []string
        for _, num := range numRow {
            cell, err := f.GetCellValue("Лист1", fmt.Sprintf("B%d", i))
        }
        if err != nil {
			fmt.Println(err)
			return nil
		}
        if cell != "" {
            fio = append(fio, strings.Trim(strings.ToLower(cell)))
		}
        
        var subdir []string

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
