package main

import (
	"database/sql"
	"fmt"
	"io"
	"log"
	"os"
	"path/filepath"
	"strings"
	"time"

	_ "github.com/mattn/go-sqlite3"
	"github.com/xuri/excelize/v2"
)

const (
	workFile   = "Кандидаты.xlsm"
	infoFile   = "Запросы по работникам.xlsx"
	database   = "persons.db"
	categoryId = 1
	statusId   = 9
	regionId   = 1
)

var basePath string = filepath.Join(getCurrentPath(), "..")
var workDir string = filepath.Join(basePath, "Кандидаты")
var archiveDir string = filepath.Join(basePath, "Персонал")
var archiveDir2 string = filepath.Join(archiveDir, "Персонал-2")
var workPath string = filepath.Join(workDir, workFile)
var infoPath string = filepath.Join(workDir, infoFile)
var databaseURI string = filepath.Join(basePath, database)

func main() {
	startTime := time.Now()

	workFileStat, err := os.Stat(workPath)
	if err != nil {
		log.Fatal("workFileStat", err)
	}

	infoFileStat, err := os.Stat(infoPath)
	if err != nil {
		log.Fatal("infoFileStat", err)
	}

	timeNow := time.Now().Truncate(24 * time.Hour)
	workFileDate := workFileStat.ModTime().Truncate(24 * time.Hour)
	infoFileDate := infoFileStat.ModTime().Truncate(24 * time.Hour)

	if timeNow.Equal(workFileDate) || timeNow.Equal(infoFileDate) {
		err := copyFile(databaseURI, filepath.Join(archiveDir, database))
		if err != nil {
			log.Fatal(err)
		}
	}
	if timeNow.Equal(infoFileDate) {
		err := copyFile(infoPath, filepath.Join(archiveDir, infoFile))
		if err != nil {
			log.Fatal(err)
		}
		parseInfoFile()
	}

	if timeNow.Equal(workFileDate) {
		err := copyFile(workPath, filepath.Join(archiveDir, workFile))
		if err != nil {
			log.Fatal(err)
		}
		parseMainFile()
	}
	fmt.Println(time.Since(startTime))
}

func copyFile(src, dest string) error {
	sourceFile, err := os.Open(src)
	if err != nil {
		return err
	}
	defer sourceFile.Close()

	destinationFile, err := os.Create(dest)
	if err != nil {
		return err
	}
	defer destinationFile.Close()

	_, err = io.Copy(destinationFile, sourceFile)
	if err != nil {
		return err
	}

	err = destinationFile.Sync()
	if err != nil {
		return err
	}

	return nil
}

func getCurrentPath() (cur string) {
	cur, err := os.Getwd()
	if err != nil {
		log.Fatal(err)
	}
	return
}

func parseInfoFile() {
	f, err := excelize.OpenFile(infoPath)
	if err != nil {
		log.Fatal(err)
	}
	defer f.Close()

	totalRows := 100000 //, _ := f.GetRows("Лист1")
	numRows := make([]int, 0, totalRows)

	for i := 2; i < totalRows; i++ {
		cell, err := f.GetCellValue("Лист1", fmt.Sprintf("%s%d", "G", i))
		if err != nil {
			log.Fatal(err)
		}
		if cell != "" {
			t, err := time.Parse("02/01/2006", cell)
			if err != nil {
				continue
			}
			if t.Format("2006-01-02") == time.Now().Format("2006-01-02") {
				numRows = append(numRows, i)
			}
		}
	}
	if len(numRows) == 0 {
		return
	}

	db, err := sql.Open("sqlite3", databaseURI)
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	stmtInsertPerson, err := db.Prepare(
		"INSERT INTO persons (fullname, birthday, `create`, category_id, region_id, status_id) VALUES (?, ?, ?, ?, ?, ?)",
	)
	if err != nil {
		log.Fatal(err)
	}
	defer stmtInsertPerson.Close()

	stmtUpdatePerson, err := db.Prepare("UPDATE persons SET `update` = ? WHERE id = ?")
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

	for _, num := range numRows {
		var candId int

		info, err := f.GetCellValue("Лист1", fmt.Sprintf("E%d", num))
		if err != nil {
			info = ""
		}

		initiator, err := f.GetCellValue("Лист1", fmt.Sprintf("F%d", num))
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
			day = time.Now()
		}
		birthday := day.Truncate(24 * time.Hour)

		deadline := time.Now()

		row := db.QueryRow(
			"SELECT id FROM persons WHERE fullname = ? AND birthday = ?",
			fullname, birthday,
		)

		err = row.Scan(&candId)
		if err == sql.ErrNoRows {
			result, err := stmtInsertPerson.Exec(
				fullname, birthday, deadline, 1, 1, 9,
			)
			if err != nil {
				log.Fatal(err)
			}
			id, _ := result.LastInsertId()
			candId = int(id)

		} else if err != nil {
			log.Fatal(err)

		} else {
			_, err := stmtUpdatePerson.Exec(
				deadline, candId,
			)
			if err != nil {
				log.Fatal(err)
			}
		}

		_, err = stmtInsertInquiry.Exec(
			info, initiator, deadline, candId,
		)
		if err != nil {
			log.Fatal(err)
		}
	}
}

func parseMainFile() {
	f, err := excelize.OpenFile(workPath)
	if err != nil {
		log.Fatal(err)
		panic(err)
	}
	defer f.Close()

	totalRows := 100000 //, _ := f.GetRows("Кандидаты")
	numRows := make([]int, 0, totalRows)

	for i := 2; i < totalRows; i++ {
		cell, err := f.GetCellValue("Кандидаты", fmt.Sprintf("%s%d", "K", i))
		if err != nil {
			log.Fatal(err)
		}
		if cell != "" {
			t, err := time.Parse("02/01/2006", cell)
			if err != nil {
				continue
			}
			if t.Format("2006-01-02") == time.Now().Format("2006-01-02") {
				numRows = append(numRows, i)
			}
		}
	}
	if len(numRows) == 0 {
		return
	}

	fio := make([]string, 0)
	for _, num := range numRows {
		cell, err := f.GetCellValue("Кандидаты", fmt.Sprintf("B%d", num))
		if err != nil {
			continue
		}
		fio = append(fio, strings.TrimSpace(cell))
	}

	workDirs, err := os.ReadDir(workDir)
	if err != nil {
		log.Fatal(err)
	}

	subdir := make([]string, 0)
	for _, dir := range workDirs {
		for _, name := range fio {
			if strings.EqualFold(dir.Name(), name) {
				subdir = append(subdir, dir.Name())
				break
			}
		}
	}

	excelPaths := make([]string, 0)
	excelFiles := make([]string, 0)
	jsonPaths := make([]string, 0)

	for _, sub := range subdir {
		subdirPath := filepath.Join(workDir, sub)

		workSubDirs, err := os.ReadDir(subdirPath)
		if err != nil {
			log.Fatal(err)
		}
		for _, file := range workSubDirs {
			switch {
			case (strings.HasPrefix(file.Name(), "Заключение") || strings.HasPrefix(file.Name(), "Результаты")) && (strings.HasSuffix(file.Name(), "xlsm") || strings.HasSuffix(file.Name(), "xlsx")):
				excelPaths = append(excelPaths, subdirPath)
				excelFiles = append(excelFiles, file.Name())

			case strings.HasSuffix(file.Name(), "json"):
				jsonPaths = append(jsonPaths, filepath.Join(subdirPath, file.Name()))
			}
		}
	}
	if len(excelPaths) > 0 {
		excelParse(excelPaths, excelFiles)
	}
	if len(jsonPaths) > 0 {
		jsonParse(jsonPaths)
	}
	for _, num := range numRows {
		for _, sub := range subdir {
			cell, err := f.GetCellValue("Кандидаты", fmt.Sprintf("B%d", num))
			if err != nil {
				continue
			}

			if strings.EqualFold(strings.TrimSpace(cell), strings.TrimSpace(sub)) {
				id, err := f.GetCellValue("Кандидаты", fmt.Sprintf("A%d", num))
				if err != nil {
					id = fmt.Sprintf("9999999%d", num)
				}

				firstChar := string([]rune(cell)[:1])
				lnk := filepath.Join(archiveDir2, firstChar, fmt.Sprintf("%s-%s", cell, id))
				err = f.SetCellHyperLink("Кандидаты", fmt.Sprintf("L%d", num), lnk, "External", excelize.HyperlinkOpts{
					Display: &lnk,
					Tooltip: &cell,
				})
				if err != nil {
					f.SetCellValue("Кандидаты", fmt.Sprintf("L%d", num), err.Error())
				}
				f.SetCellValue("Кандидаты", fmt.Sprintf("L%d", num), lnk)
				err = os.Rename(filepath.Join(workDir, sub), lnk)
				if err != nil {
					log.Fatal(err)
				}
			}
		}
	}

	db, err := sql.Open("sqlite3", databaseURI)
	if err != nil {
		log.Fatal(err)
		return
	}
	defer db.Close()

	stmtInsertPerson, err := db.Prepare(
		"INSERT INTO persons (fullname, birthday, `create`, path, category_id, region_id, status_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
	)
	if err != nil {
		log.Fatal(err)
	}
	defer stmtInsertPerson.Close()

	stmtUpdatePerson, err := db.Prepare("UPDATE persons SET path = ?, `update` = ? WHERE id = ?")
	if err != nil {
		log.Fatal(err)
	}
	defer stmtUpdatePerson.Close()

	for _, num := range numRows {
		var candId int

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
			day = time.Now()
		}
		birthday := day.Truncate(24 * time.Hour)

		row := db.QueryRow(
			"SELECT id FROM persons WHERE fullname = $1 AND birthday = $2",
			fullname, birthday,
		)

		err = row.Scan(&candId)
		if err != nil && err != sql.ErrNoRows {
			continue
		}

		if err == sql.ErrNoRows {
			result, err := stmtInsertPerson.Exec(fullname, birthday, time.Now(), url, categoryId, regionId, statusId)
			if err != nil {
				log.Fatal(err)
			}
			id, _ := result.LastInsertId()
			candId = int(id)

		} else {
			_, err = stmtUpdatePerson.Exec(url, time.Now(), candId)
			if err != nil {
				log.Fatal(err)
				return
			}
		}
	}

	f.SaveAs(filepath.Join(workDir, workFile))
}

func getConclusionId(conclusion string) int {

	db, err := sql.Open("sqlite3", databaseURI)

	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	row := db.QueryRow(
		"SELECT id FROM conclusions WHERE LOWER(conclusion) = $1",
		strings.ToLower(conclusion),
	)

	var id int
	err = row.Scan(&id)
	if err != nil {
		return 1
	}

	return id
}
