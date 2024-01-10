package main

import (
	"database/sql"
	"fmt"
	"io"
	"io/fs"
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
		fmt.Println(err)
		os.Exit(1)
	}
	workFileDate := workFileStat.ModTime().Format("2006-01-02")

	infoFileStat, err := os.Stat(infoPath)
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
	infoFileDate := infoFileStat.ModTime().Format("2006-01-02")

	var resultMainFile int
	var resultInfoFile int

	timeNow := now.Format("2006-01-02")

	if timeNow == workFileDate || timeNow == infoFileDate {
		err := copyFile(databaseURI, filepath.Join(archiveDir, database))
		if err != nil {
			fmt.Println(err)
		}
		db, err := sql.Open("sqlite3", databaseURI)
		if err != nil {
			fmt.Println(err)
			os.Exit(1)
		}
		defer db.Close()
		if timeNow == workFileDate {
			err := copyFile(workPath, filepath.Join(archiveDir, workFile))
			if err != nil {
				fmt.Println(err)
				os.Exit(1)
			}
			resultMainFile = parseMainFile(db)
		}
		if timeNow == infoFileDate {
			err := copyFile(infoPath, filepath.Join(archiveDir, infoFile))
			if err != nil {
				fmt.Println(err)
				os.Exit(1)
			}
			resultInfoFile = parseInfoFile(db)
		}
	}
	fmt.Printf("%d rows in MainFile and %d rows in InfoFile successfully scaned in %d ms",
		resultMainFile, resultInfoFile, time.Since(now).Milliseconds())
}

func parseInfoFile(db *sql.DB) int {

	stmtSelectPerson, err := db.Prepare("SELECT id FROM persons WHERE fullname = ? AND birthday = ?")
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
	defer stmtSelectPerson.Close()

	stmtInsertPerson, err := db.Prepare(
		"INSERT INTO persons (fullname, birthday, created, category_id, region_id, status_id) VALUES (?, ?, ?, ?, ?, ?)",
	)
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
	defer stmtInsertPerson.Close()

	stmtUpdatePerson, err := db.Prepare("UPDATE persons SET updated = ? WHERE id = ?")
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
	defer stmtUpdatePerson.Close()

	stmtInsertInquiry, err := db.Prepare(
		"INSERT INTO inquiries (info, initiator, deadline, person_id) VALUES (?, ?, ?, ?)",
	)
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
	defer stmtInsertInquiry.Close()

	f, err := excelize.OpenFile(infoPath)
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
	defer f.Close()

	type InfoFile struct {
		CandId     int
		Info       string
		Initiattor string
		FullName   string
		BirthDay   string
		DeadLine   time.Time
	}

	parsedRows := 10000
	var numRows = make([]int, 0, parsedRows)
	numRows = getRowNumbers(f, "Лист1", "G", parsedRows)

	for _, num := range numRows {
		var candId int

		fileInfo := InfoFile{
			Info:       parseStringCell(f, "Лист1", fmt.Sprintf("E%d", num)),
			Initiattor: parseStringCell(f, "Лист1", fmt.Sprintf("F%d", num)),
			FullName:   strings.ToUpper(parseStringCell(f, "Лист1", fmt.Sprintf("A%d", num))),
			BirthDay:   parseDateCell(f, "Лист1", fmt.Sprintf("B%d", num), "02/01/2006"),
			DeadLine:   time.Now(),
		}

		row := stmtSelectPerson.QueryRow(fileInfo.FullName, fileInfo.BirthDay)
		err = row.Scan(&candId)

		if err != nil {
			if err == sql.ErrNoRows {
				result, err := stmtInsertPerson.Exec(
					fileInfo.FullName, fileInfo.BirthDay, fileInfo.DeadLine,
					categoryId, regionId, statusId,
				)
				if err != nil {
					fmt.Println(err)
					continue
				}
				id, err := result.LastInsertId()
				if err != nil {
					fmt.Println(err)
					continue
				}
				candId = int(id)

			} else {
				fmt.Println(err)
				continue
			}

		} else {
			_, err := stmtUpdatePerson.Exec(
				fileInfo.DeadLine, candId,
			)
			if err != nil {
				fmt.Println(err)
				continue
			}
		}

		_, err = stmtInsertInquiry.Exec(
			fileInfo.Info, fileInfo.Initiattor, fileInfo.Initiattor, candId,
		)
		if err != nil {
			fmt.Println(err)
			continue
		}
	}
	return len(numRows)
}

func parseMainFile(db *sql.DB) int {
	f, err := excelize.OpenFile(workPath)
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
	defer f.Close()

	parsedRows := 100000
	var numRows = make([]int, 0, parsedRows)
	numRows = getRowNumbers(f, "Кандидаты", "K", parsedRows)

	if len(numRows) > 0 {
		fio := make([]string, 0, parsedRows)
		for _, num := range numRows {
			cell, err := f.GetCellValue("Кандидаты", fmt.Sprintf("B%d", num))
			if err != nil {
				fmt.Println(err)
				continue
			}
			fio = append(fio, strings.TrimSpace(cell))
		}

		workDirs, err := os.ReadDir(workDir)
		if err != nil {
			fmt.Println(err)
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
				fmt.Println(err)
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
			excelParse(db, excelPaths, excelFiles)
		}
		if len(jsonPaths) > 0 {
			jsonParse(db, jsonPaths)
		}

		for _, num := range numRows {
			for _, sub := range subdir {
				cell, err := f.GetCellValue("Кандидаты", fmt.Sprintf("B%d", num))
				if err != nil {
					fmt.Println(err)
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
					err = copyDir(subPath, lnk)
					if err != nil {
						fmt.Println(err)
						continue
					}
					err = os.RemoveAll(subPath)
					if err != nil {
						fmt.Println(err)
						continue
					}
				}
			}
		}

		stmtSelectPerson, err := db.Prepare("SELECT id FROM persons WHERE fullname = ? AND birthday = ?")
		if err != nil {
			fmt.Println(err)
			os.Exit(1)
		}
		defer stmtSelectPerson.Close()

		stmtInsertPerson, err := db.Prepare(
			"INSERT INTO persons (fullname, birthday, created, path, category_id, region_id, status_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
		)
		if err != nil {
			fmt.Println(err)
			os.Exit(1)
		}
		defer stmtInsertPerson.Close()

		stmtUpdatePerson, err := db.Prepare("UPDATE persons SET path = ?, updated = ? WHERE id = ?")
		if err != nil {
			fmt.Println(err)
			os.Exit(1)
		}
		defer stmtUpdatePerson.Close()

		for _, num := range numRows {
			var candId int

			url := parseStringCell(f, "Кандидаты", fmt.Sprintf("L%d", num))
			fullname := strings.ToTitle(parseStringCell(f, "Кандидаты", fmt.Sprintf("B%d", num)))
			birthday := parseDateCell(f, "Кандидаты", fmt.Sprintf("C%d", num), "02/01/2006")

			row := stmtSelectPerson.QueryRow(fullname, birthday)
			err = row.Scan(&candId)
			if err != nil && err != sql.ErrNoRows {
				fmt.Println(err)
				continue
			}

			if err == sql.ErrNoRows {
				result, err := stmtInsertPerson.Exec(fullname, birthday, time.Now(), url, categoryId, regionId, statusId)
				if err != nil {
					fmt.Println(err)
					continue
				}
				id, _ := result.LastInsertId()
				candId = int(id)

			} else {
				_, err = stmtUpdatePerson.Exec(url, time.Now(), candId)
				if err != nil {
					fmt.Println(err)
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
		fmt.Println(err)
		os.Exit(1)
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

func copyDir(src string, dest string) error {
	err := os.MkdirAll(dest, os.ModePerm)
	if err != nil {
		return err
	}

	err = filepath.WalkDir(src, func(path string, d fs.DirEntry, walkErr error) error {
		if path == src {
			return nil
		}

		relativePath, err := filepath.Rel(src, path)
		if err != nil {
			return err
		}
		destPath := filepath.Join(dest, relativePath)

		if !d.IsDir() {
			err = copyFile(path, destPath)
			if err != nil {
				return err
			}
		}
		return nil
	})
	return err
}

func getRowNumbers(f *excelize.File, listName string, collName string, parsedRows int) []int {

	numRows := make([]int, 0, parsedRows)

	for i := 2; i < parsedRows; i++ {
		cell, err := f.GetCellValue(listName, fmt.Sprintf("%s%d", collName, i))
		if err != nil {
			fmt.Println(err)
			continue
		}
		if cell != "" {
			t, err := time.Parse("02/01/2006", cell)
			if err != nil {
				// fmt.Println(err)
				continue
			}
			if t.Format("2006-01-02") == time.Now().Format("2006-01-02") {
				numRows = append(numRows, i)
			}
		}
	}
	return numRows
}

func parseStringCell(f *excelize.File, listName string, cellName string) string {
	cell, err := f.GetCellValue(listName, cellName)
	if err != nil {
		cell = err.Error()
	}
	return cell
}

func parseDateCell(f *excelize.File, listName string, cellName string, format string) string {
	cell, err := f.GetCellValue(listName, cellName)
	if err != nil {
		cell = format
	}
	day, err := time.Parse(format, cell)
	if err != nil {
		day = time.Now()
	}
	return day.Format("2006-01-02")
}

func trimmString(value string) string {
	splited := strings.Split(value, " ")
	trimmed := make([]string, 0)
	for _, item := range splited {
		if item != "" {
			trimmed = append(trimmed, strings.TrimSpace(item))
		}
	}
	return strings.Join(trimmed, " ")
}
