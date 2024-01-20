package main

import (
	"database/sql"
	"fmt"
	"io"
	"log"
	"os"
	"path/filepath"
	"strings"
	"sync"
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

var currentPath, _ = os.Getwd()
var basePath string = filepath.Join(currentPath, "..")
var logfile string = filepath.Join(basePath, "robot.log")
var databaseURI string = filepath.Join(basePath, database)
var workDir string = filepath.Join(basePath, "Кандидаты")
var workPath string = filepath.Join(workDir, workFile)
var infoPath string = filepath.Join(workDir, infoFile)
var archiveDir string = filepath.Join(basePath, "Персонал", "Персонал-2")

func main() {
	fileLog, err := os.OpenFile(logfile, os.O_RDWR|os.O_CREATE|os.O_APPEND, os.ModePerm)
	if err != nil {
		log.Fatal(err)
	}
	defer fileLog.Close()
	log.SetOutput(fileLog)

	now := time.Now()

	workFileDate, err := getFileDate(workPath)
	if err != nil {
		log.Fatal(err)
	}

	infoFileDate, err := getFileDate(infoPath)
	if err != nil {
		log.Fatal(err)
	}

	resultMainFile, resultInfoFile := chansHandler(now, workFileDate, infoFileDate)

	log.Printf("%d rows in MainFile and %d rows in InfoFile successfully scaned in %d ms",
		resultMainFile, resultInfoFile, time.Since(now).Milliseconds())
}

func getFileDate(path string) (string, error) {
	stat, err := os.Stat(path)
	if err != nil {
		return "", err
	}
	return stat.ModTime().Format("2006-01-02"), nil
}

func chansHandler(now time.Time, workFileDate string, infoFileDate string) (int, int) {
	timeNow := now.Format("2006-01-02")

	chanMain, chanInfo := make(chan int), make(chan int)

	if timeNow == workFileDate || timeNow == infoFileDate {
		err := copyFile(databaseURI, filepath.Join(archiveDir, database))
		if err != nil {
			log.Fatal(err)
		}

		db, err := sql.Open("sqlite3", databaseURI)
		if err != nil {
			log.Fatal(err)
		}
		defer db.Close()

		if timeNow == workFileDate {
			err := copyFile(workPath, filepath.Join(archiveDir, workFile))
			if err != nil {
				log.Fatal(err)
			}
			go parseMainFile(db, chanMain)
		}

		if timeNow == infoFileDate {
			err := copyFile(infoPath, filepath.Join(archiveDir, infoFile))
			if err != nil {
				log.Fatal(err)
			}
			go parseInfoFile(db, chanInfo)
		}
	}

	var resultMainFile, resultInfoFile int

	if timeNow == workFileDate {
		resultMainFile = <-chanMain
	}
	if timeNow == infoFileDate {
		resultInfoFile = <-chanInfo
	}
	return resultMainFile, resultInfoFile
}

func parseInfoFile(db *sql.DB, ch chan int) {
	queries := map[string]string{
		"selectPerson":  "SELECT id FROM persons WHERE fullname = ? AND birthday = ?",
		"insertPerson":  "INSERT INTO persons (fullname, birthday, created, category_id, region_id, status_id) VALUES (?, ?, ?, ?, ?, ?)",
		"updatePerson":  "UPDATE persons SET updated = ? WHERE id = ?",
		"insertInquiry": "INSERT INTO inquiries (info, initiator, deadline, person_id) VALUES (?, ?, ?, ?)",
	}

	f, err := excelize.OpenFile(infoPath)
	if err != nil {
		log.Fatal(err)
	}
	defer f.Close()

	var numRows []int
	for i := 1; i < 5000; i++ {
		t, err := parseDateCell(f, "Лист1", fmt.Sprintf("G%d", i))
		if err == nil && t == time.Now().Format("2006-01-02") {
			numRows = append(numRows, i)
		}
	}

	for _, num := range numRows {
		info, _ := f.GetCellValue("Лист1", fmt.Sprintf("E%d", num))
		init, _ := f.GetCellValue("Лист1", fmt.Sprintf("F%d", num))
		name, _ := f.GetCellValue("Лист1", fmt.Sprintf("A%d", num))
		fullName := strings.ToTitle(name)
		birth, err := parseDateCell(f, "Лист1", fmt.Sprintf("B%d", num))
		if err != nil {
			birth = "2006-01-02"
		}
		birthDay := birth
		deadLine := time.Now()

		var candId int
		stmts := stmtsQuery(db, queries)
		row := stmts["selectPerson"].QueryRow(fullName, birthDay)
		err = row.Scan(&candId)

		if err != nil {
			if err == sql.ErrNoRows {
				result, err := stmts["insertPerson"].Exec(
					fullName, birthDay, deadLine,
					categoryId, regionId, statusId,
				)
				if err != nil {
					log.Println(err)
				}
				id, err := result.LastInsertId()
				if err != nil {
					log.Println(err)
				}
				candId = int(id)
			} else {
				log.Println(err)
			}
		} else {
			_, err := stmts["updatePerson"].Exec(deadLine, candId)
			if err != nil {
				log.Println(err)
			}
		}

		_, err = stmts["insertInquiry"].Exec(info, init, deadLine, candId)
		if err != nil {
			log.Println(err)
		}
	}
	ch <- len(numRows)
}

func parseMainFile(db *sql.DB, ch chan int) {
	f, err := excelize.OpenFile(workPath)
	if err != nil {
		log.Fatal(err)
	}
	defer f.Close()

	var numRows = make([]int, 0)
	for i := 1; i < 50000; i++ {
		t, err := parseDateCell(f, "Кандидаты", fmt.Sprintf("%s%d", "K", i))
		if err == nil && t == time.Now().Format("2006-01-02") {
			numRows = append(numRows, i)
		}
	}

	if len(numRows) > 0 {
		fio := make([]string, 0)
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

		subdir := make([]string, 0)
		for _, dir := range workDirs {
			for _, name := range fio {
				if strings.EqualFold(dir.Name(), name) {
					subdir = append(subdir, dir.Name())
					break
				}
			}
		}

		if len(subdir) > 0 {
			var excelPaths, excelFiles, jsonPaths []string

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

			chanExcel, chanJson := make(chan int), make(chan int)

			if len(excelPaths) > 0 {
				go excelParse(db, &excelPaths, &excelFiles, chanExcel)
			}
			if len(jsonPaths) > 0 {
				go jsonParse(db, &jsonPaths, chanJson)
			}

			var parseExcel int
			var parseJson int

			if len(excelPaths) > 0 {
				parseExcel = <-chanExcel
			}
			if len(jsonPaths) > 0 {
				parseJson = <-chanJson
			}

			log.Printf("%d excel files and %d json files successfully parsed",
				parseExcel, parseJson)

			var wg sync.WaitGroup

			for _, num := range numRows {
				for _, sub := range subdir {
					wg.Add(1)
					go func(numb int, subd string) {
						cell, err := f.GetCellValue("Кандидаты", fmt.Sprintf("B%d", numb))
						if err != nil {
							log.Println(err)
						}

						if strings.EqualFold(strings.TrimSpace(cell), strings.TrimSpace(subd)) {
							id, err := f.GetCellValue("Кандидаты", fmt.Sprintf("A%d", numb))
							if err != nil {
								id = fmt.Sprintf("999%d", numb)
							}

							firstChar := string([]rune(cell)[:1])
							lnk := filepath.Join(archiveDir, firstChar, fmt.Sprintf("%s-%s", cell, id))
							err = f.SetCellHyperLink("Кандидаты", fmt.Sprintf("L%d", numb), lnk, "External", excelize.HyperlinkOpts{
								Display: &lnk,
								Tooltip: &cell,
							})
							if err != nil {
								f.SetCellValue("Кандидаты", fmt.Sprintf("L%d", numb), err.Error())
							}
							f.SetCellValue("Кандидаты", fmt.Sprintf("L%d", numb), lnk)

							subPath := filepath.Join(workDir, subd)
							err = moveDir(subPath, lnk)
							if err != nil {
								log.Println(err)
							}
						}
						wg.Done()
					}(num, sub)
				}
			}
			queries := map[string]string{
				"selectPerson": "SELECT id FROM persons WHERE fullname = ? AND birthday = ?",
				"insertPerson": "INSERT INTO persons (fullname, birthday, created, path, category_id, region_id, status_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
				"updatePerson": "UPDATE persons SET path = ?, updated = ? WHERE id = ?",
			}

			stmts := stmtsQuery(db, queries)
			for _, num := range numRows {
				var candId int

				url, _ := f.GetCellValue("Кандидаты", fmt.Sprintf("L%d", num))
				name, _ := f.GetCellValue("Кандидаты", fmt.Sprintf("B%d", num))
				fullname := strings.ToTitle(name)
				birthday, err := parseDateCell(f, "Кандидаты", fmt.Sprintf("C%d", num))
				if err != nil {
					birthday = "2006-01-02"
				}
				row := stmts["selectPerson"].QueryRow(fullname, birthday)
				err = row.Scan(&candId)
				if err != nil && err != sql.ErrNoRows {
					log.Println(err)
					continue
				}

				if err == sql.ErrNoRows {
					result, err := stmts["insertPerson"].Exec(
						fullname, birthday, time.Now(), url,
						categoryId, regionId, statusId,
					)
					if err != nil {
						log.Println(err)
						continue
					}
					id, _ := result.LastInsertId()
					candId = int(id)

				} else {
					_, err = stmts["updatePerson"].Exec(url, time.Now(), candId)
					if err != nil {
						log.Println(err)
						continue
					}
				}
			}
			wg.Wait()
			f.SaveAs(filepath.Join(workDir, workFile))
		}
	}
	ch <- len(numRows)
}

func stmtsQuery(db *sql.DB, queries map[string]string) map[string]*sql.Stmt {
	stmts := make(map[string]*sql.Stmt)
	for key, query := range queries {
		stmt, err := db.Prepare(query)
		if err != nil {
			log.Fatal(err)
		}
		defer stmt.Close()
		stmts[key] = stmt
	}
	return stmts

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
	return destinationFile.Sync()
}

func moveDir(src string, dest string) error {
	if err := os.MkdirAll(dest, os.ModePerm); err != nil {
		return err
	}

	err := filepath.WalkDir(src, func(path string, info os.DirEntry, err error) error {
		if err != nil {
			return err
		}
		relPath, err := filepath.Rel(src, path)
		if err != nil {
			return err
		}
		destPath := filepath.Join(dest, relPath)
		if info.IsDir() {
			return os.MkdirAll(destPath, os.ModePerm)
		}
		return copyFile(path, destPath)
	})
	if err != nil {
		return err
	}

	return os.RemoveAll(src)
}

func parseDateCell(f *excelize.File, listName string, cellName string) (string, error) {
	cell, err := f.GetCellValue(listName, cellName)
	if err != nil || cell == "" {
		return "", fmt.Errorf("error or empty cell")
	}

	dateFormats := []string{"01-02-06", "06/01/02", "01-02-2006", "02/01/2006", "02.01.2006"}
	for _, format := range dateFormats {
		t, err := time.Parse(format, cell)
		if err == nil {
			return t.Format("2006-01-02"), nil
		}
	}

	return "", fmt.Errorf("unable to parse date")
}
