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

	timeNow := now.Format("2006-01-02")

	var resultMainFile, resultInfoFile int

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

func parseInfoFile(db *sql.DB) int {
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
		stmts := make(map[string]*sql.Stmt)
		for key, query := range queries {
			stmt, err := db.Prepare(query)
			if err != nil {
				log.Fatal(err)
			}
			defer stmt.Close()
			stmts[key] = stmt
		}

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
			log.Println("error5", err)
		}
	}
	return len(numRows)
}

func parseMainFile(db *sql.DB) int {
	f, err := excelize.OpenFile(workPath)
	if err != nil {
		log.Fatal(err)
	}

	var numRows = make([]int, 0)
	for i := 10000; i < 50000; i++ {
		t, err := parseDateCell(f, "Кандидаты", fmt.Sprintf("%s%d", "K", i))
		if err == nil && t == time.Now().Format("2006-01-02") {
			numRows = append(numRows, i)
		}
	}

	if len(numRows) > 0 {
		queries := map[string]string{
			"selectPerson": "SELECT id FROM persons WHERE fullname = ? AND birthday = ?",
			"insertPerson": "INSERT INTO persons (fullname, birthday, created, path, category_id, region_id, status_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
			"updatePerson": "UPDATE persons SET path = ?, updated = ? WHERE id = ?",
		}

		stmts := make(map[string]*sql.Stmt)
		for key, query := range queries {
			stmt, err := db.Prepare(query)
			if err != nil {
				log.Fatal(err)
			}
			defer stmt.Close()
			stmts[key] = stmt
		}

		workDirs, err := os.ReadDir(workDir)
		if err != nil {
			log.Fatal(err)
		}

		for _, num := range numRows {
			cell, err := f.GetCellValue("Кандидаты", fmt.Sprintf("B%d", num))
			if err != nil {
				log.Println(err)
				continue
			}

			for _, dir := range workDirs {
				if strings.EqualFold(dir.Name(), cell) {

					subdirPath := filepath.Join(workDir, cell)
					filesDirs, err := os.ReadDir(subdirPath)
					if err != nil {
						log.Println(err)
						continue
					}

					for _, file := range filesDirs {
						switch {
						case (strings.HasPrefix(file.Name(), "Заключение") || strings.HasPrefix(file.Name(), "Результаты")) &&
							(strings.HasSuffix(file.Name(), "xlsm") || strings.HasSuffix(file.Name(), "xlsx")):
							excelParse(db, subdirPath, file.Name())

						case strings.HasSuffix(file.Name(), "json"):
							jsonParse(db, subdirPath, file.Name())
						}
					}

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
					} else {
						f.SetCellValue("Кандидаты", fmt.Sprintf("L%d", num), lnk)
					}

					err = moveDir(subdirPath, lnk)
					if err != nil {
						log.Println(err)
					}

					var candId int

					fullname := strings.ToTitle(cell)
					birthday, err := parseDateCell(f, "Кандидаты", fmt.Sprintf("C%d", num))
					if err != nil {
						birthday = "2006-01-02"
					}

					row := stmts["selectPerson"].QueryRow(fullname, birthday)
					err = row.Scan(&candId)
					if err != nil && err != sql.ErrNoRows {
						log.Println("Error1: ", err)
						continue
					}

					if err == sql.ErrNoRows {
						result, err := stmts["insertPerson"].Exec(
							fullname, birthday, time.Now(), lnk,
							categoryId, regionId, statusId,
						)
						if err != nil {
							log.Println(err)
							continue
						}

						id, _ := result.LastInsertId()
						candId = int(id)

					} else {
						_, err = stmts["updatePerson"].Exec(lnk, time.Now(), candId)
						if err != nil {
							log.Println(err)
							continue
						}
					}
				}
			}
		}
	}
	err = f.Save()
	if err != nil {
		log.Println(err)
	}
	return len(numRows)
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
