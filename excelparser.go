package main

import (
	"database/sql"
	"fmt"
	"log"
	"path/filepath"
	"strings"
	"time"

	_ "github.com/mattn/go-sqlite3"
	"github.com/xuri/excelize/v2"
)

type Anketa struct {
	fullname   string
	previous   string
	birthday   string
	birthplace string
	country    string
	snils      string
	inn        string
	education  string
}

type Check struct {
	workplace  string
	cronos     string
	cros       string
	document   string
	debt       string
	bankruptcy string
	bki        string
	affilation string
	internet   string
	pfo        bool
	addition   string
	conclusion int
	officer    string
	deadline   time.Time
}

type Robot struct {
	inn        string
	employee   string
	terrorist  string
	mvd        string
	courts     string
	bankruptcy string
	bki        string
}

func excelParse(db *sql.DB, excelPath string, excelFile string) {
	queries := map[string]string{
		"updatePerson":      "UPDATE persons SET fullname = ?, previous = ?, birthday = ?, birthplace = ?, country = ?, snils = ?, inn = ?, education = ?, updated = ?, category_id = ?, region_id = ?, status_id = ? WHERE id = ?",
		"updateShortPerson": "UPDATE persons SET fullname = ?, birthday = ?, updated = ?, category_id = ?, region_id = ?, status_id = ? WHERE id = ?",
		"insertShortPerson": "INSERT INTO persons (fullname, birthday, created, category_id, region_id, status_id) VALUES (?, ?, ?, ?, ?, ?)",
		"insertPerson":      "INSERT INTO persons (fullname, previous, birthday, birthplace, country, snils, inn, education, created, category_id, region_id, status_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
		"insertCheck":       "INSERT INTO checks (workplace, cronos, cros, document, debt, bankruptcy, bki, affilation, internet, pfo, addition, conclusion, officer, deadline, person_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
		"insertRobot":       "INSERT INTO robots (inn, employee, terrorist, mvd, courts, bankruptcy, bki, deadline, person_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
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

	var candId int
	var fio string
	var anketa Anketa

	f, err := excelize.OpenFile(filepath.Join(excelPath, excelFile))
	if err != nil {
		log.Println(err)
		return
	}
	defer f.Close()

	if strings.HasPrefix(excelFile, "Заключение") {
		name, _ := f.GetCellValue("Лист1", "C6")
		if name == "" {
			return
		}
		anketa.fullname = strings.ToTitle(strings.Join(strings.Fields(name), " "))
		anketa.birthday, _ = parseDateCell(f, "Лист1", "C8")
		if err != nil {
			anketa.birthday = "2006-01-02"
		}
		anketa.previous, _ = f.GetCellValue("Лист1", "C7")

		if f.SheetCount > 1 {
			fio, err = f.GetCellValue("Лист2", "K1")
			if err != nil {
				log.Println(err)
				return
			}

			if fio == "ФИО" {
				name, _ := f.GetCellValue("Лист2", "K3")
				if name == "" {
					return
				}
				anketa.fullname = strings.ToTitle(strings.Join(strings.Fields(name), " "))
				anketa.previous, _ = f.GetCellValue("Лист2", "S3")
				anketa.birthday, _ = parseDateCell(f, "Лист2", "L3")
				if err != nil {
					anketa.birthday = "2006-01-02"
				}
				anketa.birthplace, _ = f.GetCellValue("Лист2", "M3")
				anketa.country, _ = f.GetCellValue("Лист2", "T3")
				anketa.snils, _ = f.GetCellValue("Лист2", "U3")
				anketa.inn, _ = f.GetCellValue("Лист2", "V3")
				anketa.education, _ = f.GetCellValue("Лист2", "W3")
			}
		}
		var check Check
		wp1, _ := f.GetCellValue("Лист1", "D11")
		wp2, _ := f.GetCellValue("Лист1", "D12")
		wp3, _ := f.GetCellValue("Лист1", "D13")
		check.workplace = fmt.Sprintf("%s; %s; %s", wp1, wp2, wp3)
		check.cronos, _ = f.GetCellValue("Лист1", "C14")
		check.cros, _ = f.GetCellValue("Лист1", "C16")
		check.document, _ = f.GetCellValue("Лист1", "C17")
		check.debt, _ = f.GetCellValue("Лист1", "C18")
		check.bankruptcy, _ = f.GetCellValue("Лист1", "C19")
		check.bki, _ = f.GetCellValue("Лист1", "C20")
		check.affilation, _ = f.GetCellValue("Лист1", "C21")
		check.internet, _ = f.GetCellValue("Лист1", "C22")
		check.officer, _ = f.GetCellValue("Лист1", "C25")
		check.addition, _ = f.GetCellValue("Лист1", "C28")

		decision, err := f.GetCellValue("Лист1", "C23")
		if err != nil {
			decision = "Согласовано"
		}
		row := db.QueryRow(
			"SELECT id FROM conclusions WHERE LOWER(conclusion) = $1",
			strings.ToLower(decision),
		)
		err = row.Scan(&check.conclusion)
		if err != nil {
			check.conclusion = 1
		}
		check.deadline = time.Now()
		poligraf, err := f.GetCellValue("Лист1", "C26")
		if err != nil {
			poligraf = "назначено"
		}
		if strings.ToLower(poligraf) == "назначено" || poligraf == "на испытательном сроке" {
			check.pfo = true
		} else {
			check.pfo = false
		}

		result := db.QueryRow(
			"SELECT id FROM persons WHERE fullname = ? AND birthday = ?",
			anketa.fullname, anketa.birthday,
		)
		err = result.Scan(&candId)
		if err != nil {
			if err == sql.ErrNoRows {
				result, err := stmts["insertPerson"].Exec(
					anketa.fullname, anketa.previous, anketa.birthday,
					anketa.birthplace, anketa.country, anketa.snils,
					anketa.inn, anketa.education, time.Now(),
					categoryId, regionId, statusId,
				)
				if err != nil {
					log.Println(err)
					return
				}
				id, err := result.LastInsertId()
				if err != nil {
					log.Println(err)
					return
				}
				candId = int(id)
			} else {
				log.Println(err)
				return
			}

		} else {
			if fio == "" {
				_, err := stmts["updatePerson"].Exec(
					anketa.fullname, anketa.previous, anketa.birthday, anketa.birthplace,
					anketa.country, anketa.snils, anketa.inn, anketa.education,
					time.Now(), categoryId, regionId, statusId, candId,
				)
				if err != nil {
					log.Println(err)
					return
				}
			} else {
				_, err := stmts["updateShortPerson"].Exec(
					anketa.fullname, anketa.birthday, time.Now(), categoryId,
					regionId, statusId, candId,
				)
				if err != nil {
					log.Println(err)
					return
				}
			}

		}

		_, err = stmts["insertCheck"].Exec(
			check.workplace, check.cronos, check.cros, check.document, check.debt,
			check.bankruptcy, check.bki, check.affilation, check.internet,
			check.pfo, check.addition, check.conclusion, check.officer, time.Now(), candId,
		)
		if err != nil {
			log.Println(err)
			return
		}

	} else {
		var robot Robot
		name, _ := f.GetCellValue("Лист1", "B4")
		anketa.fullname = strings.ToTitle(strings.Join(strings.Fields(name), " "))
		anketa.birthday, err = parseDateCell(f, "Лист1", "B5")
		if err != nil {
			anketa.birthday = "2006-01-02"
		}

		robot.employee, _ = f.GetCellValue("Лист1", "B27")
		robot.terrorist, _ = f.GetCellValue("Лист1", "B17")
		robot.inn, _ = f.GetCellValue("Лист1", "B18")
		bnkrpt, _ := f.GetCellValue("Лист1", "B20")
		bnkrpt2, _ := f.GetCellValue("Лист1", "B21")
		bnkrpt3, _ := f.GetCellValue("Лист1", "B22")
		robot.bankruptcy = fmt.Sprintf("%s, %s, %s", bnkrpt, bnkrpt2, bnkrpt3)
		robot.mvd, _ = f.GetCellValue("Лист1", "B23")
		robot.courts, _ = f.GetCellValue("Лист1", "B24")
		robot.bki, _ = f.GetCellValue("Лист1", "B25")

		result := db.QueryRow(
			"SELECT id FROM persons WHERE fullname = ? AND birthday = ?",
			anketa.fullname, anketa.birthday,
		)
		err = result.Scan(&candId)
		if err != nil {
			if err == sql.ErrNoRows {
				result, err := stmts["insertShortPerson"].Exec(
					anketa.fullname, anketa.birthday, time.Now(),
					categoryId, regionId, statusId,
				)
				if err != nil {
					log.Println(err)
					return
				}
				id, err := result.LastInsertId()
				if err != nil {
					log.Println(err)
					return
				}
				candId = int(id)
			} else {
				log.Println(err)
				return
			}

		} else {
			_, err := stmts["updateShortPerson"].Exec(
				anketa.fullname, anketa.birthday, time.Now(),
				categoryId, regionId, statusId, candId,
			)
			if err != nil {
				log.Println(err)
				return
			}
		}

		_, err = stmts["insertRobot"].Exec(robot.inn, robot.employee, robot.terrorist,
			robot.mvd, robot.courts, robot.bankruptcy, robot.bki, time.Now(), candId)
		if err != nil {
			log.Println(err)
			return
		}
	}
}
