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
var databaseURI string = filepath.Join(basePath, database)
var workDir string = filepath.Join(basePath, "Кандидаты")
var workPath string = filepath.Join(workDir, workFile)
var infoPath string = filepath.Join(workDir, infoFile)
var archiveDir string = filepath.Join(basePath, "Персонал", "Персонал-2")

func main() {
	now := time.Now()

	workFileStat, err := os.Stat(workPath)
	if err != nil {
		log.Fatal(err)
	}
	workFileDate := workFileStat.ModTime().Format("2006-01-02")

	infoFileStat, err := os.Stat(infoPath)
	if err != nil {
		log.Fatal(err)
	}
	infoFileDate := infoFileStat.ModTime().Format("2006-01-02")

	var resultMainFile int
	var resultInfoFile int

	db, err := sql.Open("sqlite3", databaseURI)
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	timeNow := now.Format("2006-01-02")

	if timeNow == workFileDate || timeNow == infoFileDate {
		err := copyFile(databaseURI, filepath.Join(archiveDir, database))
		if err != nil {
			log.Fatal(err)
		}

		if timeNow == workFileDate {
			err := copyFile(workPath, filepath.Join(archiveDir, workFile))
			if err != nil {
				log.Fatal(err)
			}
			resultMainFile = parseMainFile(db)
		}

		if timeNow == infoFileDate {
			err := copyFile(infoPath, filepath.Join(archiveDir, infoFile))
			if err != nil {
				log.Fatal(err)
			}
			resultInfoFile = parseInfoFile(db)
		}
	}
	fmt.Printf("%d rows in MainFile and %d rows in InfoFile successfully scaned in %d ms",
		resultMainFile, resultInfoFile, time.Since(now).Milliseconds())
}

func parseInfoFile(db *sql.DB) int {
	type InfoFile struct {
		CandId     int
		Info       string
		Initiattor string
		FullName   string
		BirthDay   string
		DeadLine   time.Time
	}

	stmtSelectPerson, err := db.Prepare("SELECT id FROM persons WHERE fullname = ? AND birthday = ?")
	if err != nil {
		log.Fatal(err)
	}
	defer stmtSelectPerson.Close()

	stmtInsertPerson, err := db.Prepare(
		"INSERT INTO persons (fullname, birthday, created, category_id, region_id, status_id) VALUES (?, ?, ?, ?, ?, ?)",
	)
	if err != nil {
		log.Fatal(err)
	}
	defer stmtInsertPerson.Close()

	stmtUpdatePerson, err := db.Prepare("UPDATE persons SET updated = ? WHERE id = ?")
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

	f, err := excelize.OpenFile(infoPath)
	if err != nil {
		log.Fatal(err)
	}
	defer f.Close()

	parsedRows := 10000
	var numRows = make([]int, 0, parsedRows)
	for i := 1; i < parsedRows; i++ {
		t, err := parseDateCell(f, "Лист1", fmt.Sprintf("G%d", i))
		if err == nil && t == time.Now().Format("2006-01-02") {
			numRows = append(numRows, i)
		}
	}

	for _, num := range numRows {
		birth, err := parseDateCell(f, "Лист1", fmt.Sprintf("B%d", num))
		if err != nil {
			birth = "2006-01-02"
		}
		fileInfo := InfoFile{
			Info:       parseStringCell(f, "Лист1", fmt.Sprintf("E%d", num)),
			Initiattor: parseStringCell(f, "Лист1", fmt.Sprintf("F%d", num)),
			FullName:   strings.ToUpper(parseStringCell(f, "Лист1", fmt.Sprintf("A%d", num))),
			BirthDay:   birth,
			DeadLine:   time.Now(),
		}

		row := stmtSelectPerson.QueryRow(fileInfo.FullName, fileInfo.BirthDay)
		err = row.Scan(&fileInfo.CandId)

		if err != nil {
			if err == sql.ErrNoRows {
				result, err := stmtInsertPerson.Exec(
					fileInfo.FullName, fileInfo.BirthDay, fileInfo.DeadLine,
					categoryId, regionId, statusId,
				)
				if err != nil {
					log.Println(err)
					continue
				}
				id, err := result.LastInsertId()
				if err != nil {
					log.Println(err)
					continue
				}
				fileInfo.CandId = int(id)

			} else {
				log.Println(err)
				continue
			}

		} else {
			_, err := stmtUpdatePerson.Exec(
				fileInfo.DeadLine, fileInfo.CandId,
			)
			if err != nil {
				log.Println(err)
				continue
			}
		}

		_, err = stmtInsertInquiry.Exec(
			fileInfo.Info, fileInfo.Initiattor, fileInfo.Initiattor, fileInfo.CandId,
		)
		if err != nil {
			log.Println(err)
			continue
		}
	}
	return len(numRows)
}

func parseMainFile(db *sql.DB) int {
	f, err := excelize.OpenFile(workPath)
	if err != nil {
		log.Fatal(err)
	}
	defer f.Close()

	parsedRows := 100000
	var numRows = []int{}
	for i := 1; i < parsedRows; i++ {
		t, err := parseDateCell(f, "Кандидаты", fmt.Sprintf("%s%d", "K", i))
		if err == nil && t == time.Now().Format("2006-01-02") {
			numRows = append(numRows, i)
		}
	}

	if len(numRows) > 0 {
		fio := make([]string, 0, parsedRows)
		for _, num := range numRows {
			cell, err := f.GetCellValue("Кандидаты", fmt.Sprintf("B%d", num))
			if err != nil {
				log.Println(err)
				continue
			}
			fio = append(fio, strings.TrimSpace(cell))
		}

		workDirs, err := os.ReadDir(workDir)
		if err != nil {
			log.Println(err)
		}

		subdir := make([]string, 0, parsedRows)
		for _, dir := range workDirs {
			for _, name := range fio {
				if strings.EqualFold(dir.Name(), name) {
					subdir = append(subdir, dir.Name())
					continue
				}
			}
		}

		excelPaths := make([]string, 0, parsedRows)
		excelFiles := make([]string, 0, parsedRows)
		jsonPaths := make([]string, 0, parsedRows)

		for _, sub := range subdir {
			subdirPath := filepath.Join(workDir, sub)
			workSubDirs, err := os.ReadDir(subdirPath)
			if err != nil {
				log.Println(err)
				continue
			}
			for _, file := range workSubDirs {
				switch {
				case (strings.HasPrefix(file.Name(), "Заключение") || strings.HasPrefix(file.Name(), "Результаты")) &&
					(strings.HasSuffix(file.Name(), "xlsm") || strings.HasSuffix(file.Name(), "xlsx")):
					excelPaths = append(excelPaths, subdirPath)
					excelFiles = append(excelFiles, file.Name())

				case strings.HasSuffix(file.Name(), "json"):
					jsonPaths = append(jsonPaths, filepath.Join(subdirPath, file.Name()))
				}
			}
		}

		if len(excelPaths) > 0 {
			excelParse(db, &excelPaths, &excelFiles)
		}
		if len(jsonPaths) > 0 {
			jsonParse(db, &jsonPaths)
		}

		for _, num := range numRows {
			for _, sub := range subdir {
				cell, err := f.GetCellValue("Кандидаты", fmt.Sprintf("B%d", num))
				if err != nil {
					log.Println(err)
					continue
				}

				if strings.EqualFold(strings.TrimSpace(cell), strings.TrimSpace(sub)) {
					id, err := f.GetCellValue("Кандидаты", fmt.Sprintf("A%d", num))
					if err != nil {
						id = fmt.Sprintf("999%d", num)
					}

					firstChar := string([]rune(cell)[:1])
					lnk := filepath.Join(archiveDir, firstChar, fmt.Sprintf("%s-%s", cell, id))
					err = f.SetCellHyperLink("Кандидаты", fmt.Sprintf("L%d", num), lnk, "External", excelize.HyperlinkOpts{
						Display: &lnk,
						Tooltip: &cell,
					})
					if err != nil {
						f.SetCellValue("Кандидаты", fmt.Sprintf("L%d", num), err.Error())
					}
					f.SetCellValue("Кандидаты", fmt.Sprintf("L%d", num), lnk)

					subPath := filepath.Join(workDir, sub)
					err = moveDir(subPath, lnk)
					if err != nil {
						log.Println(err)
						continue
					}
				}
			}
		}

		stmtSelectPerson, err := db.Prepare("SELECT id FROM persons WHERE fullname = ? AND birthday = ?")
		if err != nil {
			log.Fatal(err)
		}
		defer stmtSelectPerson.Close()

		stmtInsertPerson, err := db.Prepare(
			"INSERT INTO persons (fullname, birthday, created, path, category_id, region_id, status_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
		)
		if err != nil {
			log.Fatal(err)
		}
		defer stmtInsertPerson.Close()

		stmtUpdatePerson, err := db.Prepare("UPDATE persons SET path = ?, updated = ? WHERE id = ?")
		if err != nil {
			log.Fatal(err)
		}
		defer stmtUpdatePerson.Close()

		for _, num := range numRows {
			var candId int

			url := parseStringCell(f, "Кандидаты", fmt.Sprintf("L%d", num))
			fullname := strings.ToTitle(parseStringCell(f, "Кандидаты", fmt.Sprintf("B%d", num)))
			birthday, err := parseDateCell(f, "Кандидаты", fmt.Sprintf("C%d", num))
			if err != nil {
				birthday = "2006-01-02"
			}
			row := stmtSelectPerson.QueryRow(fullname, birthday)
			err = row.Scan(&candId)
			if err != nil && err != sql.ErrNoRows {
				log.Println(err)
				continue
			}

			if err == sql.ErrNoRows {
				result, err := stmtInsertPerson.Exec(fullname, birthday, time.Now(), url, categoryId, regionId, statusId)
				if err != nil {
					log.Println(err)
					continue
				}
				id, _ := result.LastInsertId()
				candId = int(id)

			} else {
				_, err = stmtUpdatePerson.Exec(url, time.Now(), candId)
				if err != nil {
					log.Println(err)
					continue
				}
			}
		}
		f.SaveAs(filepath.Join(workDir, workFile))
	}
	return len(numRows)
}

func getCurrentPath() (cur string) {
	cur, err := os.Getwd()
	if err != nil {
		log.Fatal(err)
	}
	return
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
func moveDir(src string, dest string) error {
	if err := os.MkdirAll(dest, os.ModePerm); err != nil {
		return err
	}

	srcDir, err := os.ReadDir(src)
	if err != nil {
		return err
	}

	for _, f := range srcDir {
		if f.IsDir() {
			err = moveDir(filepath.Join(src, f.Name()), filepath.Join(dest, f.Name()))
			if err != nil {
				return err
			}
		} else {
			err = copyFile(filepath.Join(src, f.Name()), filepath.Join(dest, f.Name()))
			if err != nil {
				return err
			}
		}
	}

	return os.RemoveAll(src)
}

func parseStringCell(f *excelize.File, listName string, cellName string) string {
	cell, err := f.GetCellValue(listName, cellName)
	if err != nil {
		cell = err.Error()
	}
	return cell
}

func parseDateCell(f *excelize.File, listName string, cellName string) (string, error) {
	cell, err := f.GetCellValue(listName, cellName)
	if err != nil || cell == "" {
		return time.Now().Format("2006-01-02"), fmt.Errorf("error or empty cell")
	}

	dateFormats := []string{"01-02-06", "06/01/02", "01-02-2006", "02/01/2006", "02.01.2006"}
	for _, format := range dateFormats {
		t, err := time.Parse(format, cell)
		if err == nil {
			return t.Format("2006-01-02"), nil
		}
	}

	return time.Now().Format("2006-01-02"), fmt.Errorf("unable to parse date")
}
