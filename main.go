package main

import (
	"database/sql"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/mattn/go-sqlite3"
	"github.com/xuri/excelize/v2"
)

type regisry struct {
	id        int
	info      string
	initiator string
	fullname  string
	decision  string
	url       string
	birthday  time.Time
	deadline  time.Time
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

	if time.Now().Truncate(24*time.Hour).Equal(workFileDate) || time.Now().Truncate(24*time.Hour).Equal(infoFileDate) {
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

func getNums(fileName, colName string) []int {
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
		f, err := excelize.OpenFile(infoPath)
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
				fullname, birthday,
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
		if err := f.Close(); err != nil {
			fmt.Println(err)
			return
		}
		var fio []string
		for _, num := range numRow {
			cell, err := f.GetCellValue("Кандидаты", fmt.Sprintf("B%d", i))
		}
		if err != nil {
			fmt.Println(err)
			return nil
		}
		if cell != "" {
			fio = append(fio, strings.Trim(strings.ToLower(cell)))
		}

		var subdir []string
		for _, dir := range os.ReadDir(workPath) {

			for _, name := range fio {

				if strings.ToLower(dir) == strings.ToLower(name) {
					subdir = append(subdir, dir)
				}
			}
		}

		// получаем список путей к файлам Заключений
		if len(subdir) > 0 {
			var excelPath []string
			var jsonPath []string

			for _, sub := range subdir {
				subdirPath := filepath.Join(workPath, sub)

				for _, file := range os.ReadDir(subdirPath) {

					if (strings.HasPrefix(file, "Заключение") && strings.HasPrefix(file, "Результаты")) || (strings.HasSuffix(file, "xlsm") && strings.HasSuffix(file, "xlsx")) {
						excelPath = append(excelPath, filepath.Join(subdirPath, sub, file))

					} else if strings.HasSuffix(file, "json") {
						jsonPath = append(jsonPath, subdirPath, sub, file)
					}
				}
			}
			// parse files and send info to database
			if len(excelPath) > 0 {
				excelParse(excel_path)
			}
			if len(jsonPath) {
				jsonParse(json_path)
			}

			// create url and move folders to archive
			for _, num := range numRow {
				for _, sub := range subdir {
					cell, err := f.GetCellValue("Кандидаты", fmt.Sprintf("%B%d", num))
					if err != nil {
						fmt.Println(err)
						return nil
					}
					if strings.ToLower(strings.Trim(cell)) == strings.ToLower(strings.Trim(sub)) {
						id, err := f.GetCellValue("Кандидаты", fmt.Sprintf("%A%d", num))
						lnk := filepath.Join(archiveDir2, cell[0:1], fmt.Sprintf("%s-%s", cell, id))
						f.SetCellValue("Кандидаты", lnk)
						os.Rename(filepath.Join(workDir, sub), lnk)
					}
				}
			}
			screenRegistryData(numRow)
		}
		f.saveAs(workFile)
	} else {
		f.Close()
	}
}

func screenRegistryData(numRow []string) {
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
		decision, _ := f.GetCellValue("Кандидаты", fmt.Sprintf("J%d", num))
		url, _ := f.GetCellValue("Кандидаты", fmt.Sprintf("L%d", num))
		fullname, _ := f.GetCellValue("Кандидаты", fmt.Sprintf("B%d", num))
		birth, _ := f.GetCellValue("Кандидаты", fmt.Sprintf("C%d", num))
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
			"SELECT id, fullname, birrthday FROM persons WHERE fullname = $1 AND birthday = $2",
			fullname, birthday,
		)
		cand := person{}
		err = row.Scan(&cand.id, &cand.fullname, &cand.birthday, &cand.decision, &cand.url)
		if err != nil || err == sql.ErrNoRows {
			return
		}
		if err == sql.ErrNoRows {
			row = db.Exec(
				"INSERT INTO persons (fullname, birthday, path)",
				fullname, birthday, url,
			)
			db.Exec(
				"UPDATE checks SET conclusion_id = $1, deadline = $2, person_id = $3)",
				getConclusionId(cand.decision), deadline, row.lastRowId,
			)
		} else {
			db.Exec(
				"UPDATE persons SET path = $1 WHERE id = $2",
				url, cand.id,
			)
		}
	}
}

func getConclusionId(conclusion string) {
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
		"SELECT id conclusions WHERE LOWER conclusion = $2",
		conclusion,
	)
	if err != nil {
		fmt.Println(err)
		return
	}
	if row > 0 {
		return row
	}
	return 1
}
