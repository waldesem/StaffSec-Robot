package main

import (
	"database/sql"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strings"
	"time"

	_ "github.com/mattn/go-sqlite3"
	"github.com/xuri/excelize/v2"
)

type registry struct {
	id       int
	fullname string
	decision string
	url      string
	birthday time.Time
	deadline time.Time
}

const (
	workFile = "Кандидаты.xlsm"
	infoFile = "Запросы по работникам.xlsx"
	database = "personal.db"
)

var basePath string = filepath.Join(getCurrentPath(), "..")
var workDir string = filepath.Join(basePath, "Кандидаты")
var archiveDir string = filepath.Join(basePath, "Персонал")
var archiveDir2 string = filepath.Join(archiveDir, "Персонал-2")
var workPath string = filepath.Join(workDir, workFile)
var infoPath string = filepath.Join(workDir, infoFile)
var databaseURI string = "sqlite:///" + filepath.Join(basePath, database)

func main() {
	workFileStat, err := os.Stat(workPath)
	if err != nil {
		log.Fatal("workFileStat", err)
	}

	infoFileStat, err := os.Stat(infoPath)
	if err != nil {
		log.Fatal("infoFileStat", err)
	}

	workFileDate := workFileStat.ModTime().Truncate(24 * time.Hour)
	infoFileDate := infoFileStat.ModTime().Truncate(24 * time.Hour)
	timeNow := time.Now().Truncate(24 * time.Hour)

	if timeNow.Equal(workFileDate) || timeNow.Equal(infoFileDate) {
		moveFile(databaseURI, filepath.Join(archiveDir, database))
	}
	if timeNow.Equal(infoFileDate) {
		moveFile(infoPath, filepath.Join(archiveDir, infoFile))
		parseMainFile()
	}
	if timeNow.Equal(workFileDate) {
		moveFile(workPath, filepath.Join(archiveDir, workFile))
		parseInfoFile()
	}
}

func moveFile(src, dest string) {
	err := os.Rename(src, dest)
	if err != nil {
		log.Fatal("moveFile", err)
	}
}

func getCurrentPath() (cur string) {
	cur, err := os.Getwd()
	if err != nil {
		fmt.Println(err)
		panic(err)
	}
	return
}

func getNums(fileName, colName string) []int {
	f, err := excelize.OpenFile(fileName)

	if err != nil {
		log.Fatal(err)
		panic(err)
	}

	defer f.Close()

	totalRows, _ := f.GetRows("Лист1")
	numRows := make([]int, 0, len(totalRows))

	for i := 1; i < len(totalRows); i++ {
		cell, err := f.GetCellValue("Лист1", fmt.Sprintf("%s%d", colName, i))
		if err != nil {
			log.Fatal(err)
		}
		if cell != "" {
			t, err := time.Parse("02/01/2006", cell)
			if err != nil {
				log.Fatal(err)
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
			log.Fatal(err)
		}
		defer f.Close()

		db, err := sql.Open("sqlite3", databaseURI)
		if err != nil {
			log.Fatal(err)
		}
		defer db.Close()

		stmtInsertPerson, err := db.Prepare(
			"INSERT INTO persons (fullname, birthday, create, category_id, region_id, status_id) VALUES (?, ?, ?, ?, ?, ?)",
		)
		if err != nil {
			log.Fatal(err)
		}
		defer stmtInsertPerson.Close()

		stmtUpdatePerson, err := db.Prepare("UPDATE persons SET update = ? WHERE id = ?")
		if err != nil {
			log.Fatal(err)
		}
		defer stmtUpdatePerson.Close()

		stmtInsertInquiry, err := db.Prepare(
			"INSERT INTO inquiries (info, initiator, deadline, person_id) VALUES (?, ?, ?, ?)",
		)
		if err != nil {
			log.Fatal(err)
		}
		defer stmtInsertInquiry.Close()

		for _, num := range numRow {
			info, err := f.GetCellValue("Лист1", fmt.Sprintf("C%d", num))
			if err != nil {
				info = ""
			}
			initiator, err := f.GetCellValue("Лист1", fmt.Sprintf("D%d", num))
			if err != nil {
				initiator = ""
			}
			fullname, err := f.GetCellValue("Лист1", fmt.Sprintf("A%d", num))
			if err != nil {
				fullname = err.Error()
			}
			birth, err := f.GetCellValue("Лист1", fmt.Sprintf("B%d", num))
			if err != nil {
				birth = "02/01/2006"
			}
			day, err := time.Parse("02/01/2006", birth)
			if err != nil {
				day = time.Now().Truncate(24 * time.Hour)
			}
			birthday := day.Local()
			deadline := time.Now().Truncate(24 * time.Hour)

			row := db.QueryRow(
				"SELECT full_name, birthday FROM candidates WHERE full_name = ? AND birthday = ?",
				fullname, birthday,
			)

			cand := registry{}
			err = row.Scan(&cand.id, &cand.fullname, &cand.birthday)

			if err == sql.ErrNoRows {
				result, err := stmtInsertPerson.Exec(
					cand.fullname, cand.birthday, cand.deadline, 1, 1, 9,
				)
				if err != nil {
					log.Fatal(err)
				}
				id, _ := result.LastInsertId()
				cand.id = int(id)

			} else if err != nil {
				log.Fatal(err)

			} else {
				_, err := stmtUpdatePerson.Exec(
					deadline, cand.id,
				)
				if err != nil {
					log.Fatal(err)
				}
			}

			_, err = stmtInsertInquiry.Exec(
				info, initiator, cand.deadline, cand.id,
			)
			if err != nil {
				log.Fatal(err)
			}
		}
	}
}

func parseMainFile() {
	numRow := getNums(workPath, "K")
	if len(numRow) == 0 {
		return
	}

	f, err := excelize.OpenFile(workFile)
	if err != nil {
		log.Fatal(err)
	}
	defer f.Close()

	fio := make([]string, 0)
	for _, num := range numRow {
		cell, err := f.GetCellValue("Кандидаты", fmt.Sprintf("B%d", num))
		if err != nil {
			cell = ""
		}
		if cell != "" {
			fio = append(fio, strings.TrimSpace(strings.ToLower(cell)))
		}
	}

	workDirs, err := os.ReadDir(workPath)
	if err != nil {
		log.Fatal(err)
	}

	subdir := make([]string, 0)
	for _, dir := range workDirs {
		for _, name := range fio {
			if strings.ToLower(dir.Name()) == strings.ToLower(name) {
				subdir = append(subdir, dir.Name())
				break
			}
		}
	}

	excelPath := make([]string, 0)
	jsonPath := make([]string, 0)

	for _, sub := range subdir {
		subdirPath := filepath.Join(workPath, sub)

		workSubDirs, err := os.ReadDir(subdirPath)
		if err != nil {
			log.Fatal(err)
		}
		for _, file := range workSubDirs {
			switch {
			case (strings.HasPrefix(file.Name(), "Заключение") || strings.HasPrefix(file.Name(), "Результаты")):
				excelPath = append(excelPath, filepath.Join(subdirPath, file.Name()))

			case strings.HasSuffix(file.Name(), "xlsm") || strings.HasSuffix(file.Name(), "xlsx"):
				excelPath = append(excelPath, filepath.Join(subdirPath, file.Name()))

			case strings.HasSuffix(file.Name(), "json"):
				jsonPath = append(jsonPath, filepath.Join(subdirPath, file.Name()))
			}
		}
	}
	// if len(excelPath) > 0 {
	// 	excelParse(excelPath)
	// }
	// if len(jsonPath) > 0 {
	// 	jsonParse(jsonPath)
	// }
	for _, num := range numRow {
		for _, sub := range subdir {
			cell, err := f.GetCellValue("Кандидаты", fmt.Sprintf("%B%d", num))
			if err != nil {
				fmt.Println(err)
				panic(err)
			}
			if strings.EqualFold(strings.TrimSpace(cell), strings.TrimSpace(sub)) {

				id, err := f.GetCellValue("Кандидаты", fmt.Sprintf("%A%d", num))
				if err != nil {
					id = fmt.Sprintf("9999999%d", num)
				}

				lnk := filepath.Join(archiveDir2, cell[:1], fmt.Sprintf("%s-%s", cell, id))
				f.SetCellValue("Кандидаты", fmt.Sprintf("%A%d", num), lnk)

				os.Rename(filepath.Join(workDir, sub), lnk)
			}
		}
	}

	screenRegistryData(numRow)

	f.SaveAs(workFile)
}

func screenRegistryData(numRow []int) {
	f, err := excelize.OpenFile(workPath)
	if err != nil {
		log.Println(err)
		return
	}
	defer f.Close()

	db, err := sql.Open("sqlite3", databaseURI)
	if err != nil {
		log.Fatal(err)
		return
	}
	defer db.Close()

	stmtInsertPerson, err := db.Prepare("INSERT INTO persons (fullname, birthday, path) VALUES (?, ?, ?)")
	if err != nil {
		log.Fatal(err)
	}

	stmtUpdateCheck, err := db.Prepare("UPDATE checks SET conclusion_id = ?, deadline = ? WHERE person_id = ?")
	if err != nil {
		log.Fatal(err)
	}

	stmtUpdatePerson, err := db.Prepare("UPDATE persons SET path = ? WHERE id = ?")
	if err != nil {
		log.Fatal(err)
	}

	for _, num := range numRow {
		decision, err := f.GetCellValue("Кандидаты", fmt.Sprintf("J%d", num))
		if err != nil {
			decision = "Согласовано"
		}
		url, err := f.GetCellValue("Кандидаты", fmt.Sprintf("L%d", num))
		if err != nil {
			url = ""
		}
		fullname, err := f.GetCellValue("Кандидаты", fmt.Sprintf("B%d", num))
		if err != nil {
			fullname = err.Error()
		}
		birth, err := f.GetCellValue("Кандидаты", fmt.Sprintf("C%d", num))
		if err != nil {
			birth = "02/01/2006"
		}
		day, err := time.Parse("02/01/2006", birth)
		if err != nil {
			day = time.Now().Truncate(24 * time.Hour)
		}
		birthday := day.Local()
		deadline := time.Now().Truncate(24 * time.Hour)

		row := db.QueryRow(
			"SELECT id, fullname, birrthday FROM persons WHERE fullname = $1 AND birthday = $2",
			fullname, birthday,
		)
		cand := registry{}
		err = row.Scan(&cand.id, &cand.fullname, &cand.birthday, &cand.url)

		if err != nil && err != sql.ErrNoRows {
			log.Println(err)
			return
		}

		if err == sql.ErrNoRows {
			ins, err := stmtInsertPerson.Exec(fullname, birthday, url)
			if err != nil {
				log.Fatal(err)
				return
			}
			insId, err := ins.LastInsertId()
			if err != nil {
				log.Fatal(err)
				return
			}
			_, err = stmtUpdateCheck.Exec(getConclusionId(decision), deadline, insId)
			if err != nil {
				log.Fatal(err)
				return
			}

		} else {
			_, err = stmtUpdatePerson.Exec(url, cand.id)
			if err != nil {
				log.Fatal(err)
				return
			}
		}
	}
}

func getConclusionId(conclusion string) int {

	db, err := sql.Open("sqlite3", databaseURI)

	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	row := db.QueryRow(
		"SELECT id FROM conclusions WHERE LOWER(conclusion) = $1",
		conclusion,
	)

	var id int
	err = row.Scan(&id)
	if err != nil {
		log.Println(err)
		return 1
	}

	return id
}
