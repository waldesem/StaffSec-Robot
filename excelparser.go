package main

import (
	"database/sql"
	"fmt"
	"os"
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

func excelParse(db *sql.DB, excelPaths []string, excelFiles []string) {
	stmtUpdatePerson, err := db.Prepare("UPDATE persons SET fullname = ?, previous = ?, birthday = ?, birthplace = ?, country = ?, snils = ?, inn = ?, education = ?, updated = ?, category_id = ?, region_id = ?, status_id = ? WHERE id = ?")
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
	defer stmtUpdatePerson.Close()

	stmtShortUpdatePerson, err := db.Prepare("UPDATE persons SET fullname = ?, birthday = ?, updated = ?, category_id = ?, region_id = ?, status_id = ? WHERE id = ?")
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
	defer stmtUpdatePerson.Close()

	stmtShortInsertPerson, err := db.Prepare("INSERT INTO persons (fullname, birthday, created, category_id, region_id, status_id) VALUES (?, ?, ?, ?, ?, ?)")
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
	defer stmtShortInsertPerson.Close()

	stmtInsertPerson, err := db.Prepare("INSERT INTO persons (fullname, previous, birthday, birthplace, country, snils, inn, education, created, category_id, region_id, status_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
	defer stmtInsertPerson.Close()

	stmtInsertCheck, err := db.Prepare("INSERT INTO checks (workplace, cronos, cros, document, debt, bankruptcy, bki, affilation, internet, pfo, addition, conclusion, officer, deadline, person_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
	defer stmtInsertCheck.Close()

	stmtInsertRobot, err := db.Prepare("INSERT INTO robots (inn, employee, terrorist, mvd, courts, bankruptcy, bki, deadline, person_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)")
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
	defer stmtInsertRobot.Close()

	for idx, file := range excelFiles {
		var candId int
		var fio string
		var anketa Anketa
		var check Check
		var robot Robot

		f, err := excelize.OpenFile(filepath.Join(excelPaths[idx], file))
		if err != nil {
			fmt.Println(err)
			continue
		}

		defer f.Close()
		if strings.HasPrefix(file, "Заключение") {
			anketa.fullname = strings.ToTitle(trimmString(parseStringCell(f, "Лист1", "C6")))
			anketa.birthday = parseDateCell(f, "Лист1", "C8", "02.01.2006")
			anketa.previous = parseStringCell(f, "Лист1", "C7")

			if f.SheetCount > 1 {
				fio, err = f.GetCellValue("Лист2", "K1")
				if err != nil {
					fmt.Println(err)
					continue
				}

				if fio == "ФИО" {
					anketa.fullname = strings.ToTitle(trimmString(parseStringCell(f, "Лист2", "K3")))
					anketa.previous = parseStringCell(f, "Лист2", "S3")
					anketa.birthday = parseDateCell(f, "Лист2", "L3", "02.01.2006")
					anketa.birthplace = parseStringCell(f, "Лист2", "M3")
					anketa.country = parseStringCell(f, "Лист2", "T3")
					anketa.snils = parseStringCell(f, "Лист2", "U3")
					anketa.inn = parseStringCell(f, "Лист2", "V3")
					anketa.education = parseStringCell(f, "Лист2", "W3")
				}
			}

			wp1 := parseStringCell(f, "Лист1", "D11")
			wp2 := parseStringCell(f, "Лист1", "D12")
			wp3 := parseStringCell(f, "Лист1", "D13")
			check.workplace = fmt.Sprintf("%s; %s; %s", wp1, wp2, wp3)
			check.cronos = parseStringCell(f, "Лист1", "C14")
			check.cros = parseStringCell(f, "Лист1", "C16")
			check.document = parseStringCell(f, "Лист1", "C17")
			check.debt = parseStringCell(f, "Лист1", "C18")
			check.bankruptcy = parseStringCell(f, "Лист1", "C19")
			check.bki = parseStringCell(f, "Лист1", "C20")
			check.affilation = parseStringCell(f, "Лист1", "C21")
			check.internet = parseStringCell(f, "Лист1", "C22")
			check.officer = parseStringCell(f, "Лист1", "C25")
			check.addition = parseStringCell(f, "Лист1", "C28")

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
					result, err := stmtInsertPerson.Exec(
						anketa.fullname, anketa.previous, anketa.birthday, anketa.birthplace, anketa.country, anketa.snils, anketa.inn, anketa.education, time.Now(), categoryId, regionId, statusId,
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
				if fio == "" {
					_, err := stmtUpdatePerson.Exec(
						anketa.fullname, anketa.previous, anketa.birthday, anketa.birthplace, anketa.country, anketa.snils, anketa.inn, anketa.education, time.Now(), categoryId, regionId, statusId, candId,
					)
					if err != nil {
						fmt.Println(err)
						continue
					}
				} else {
					_, err := stmtShortUpdatePerson.Exec(
						anketa.fullname, anketa.birthday, time.Now(), categoryId, regionId, statusId, candId,
					)
					if err != nil {
						fmt.Println(err)
						continue
					}
				}

			}

			_, err = stmtInsertCheck.Exec(
				check.workplace, check.cronos, check.cros, check.document, check.debt, check.bankruptcy, check.bki, check.affilation, check.internet, check.pfo, check.addition, check.conclusion, check.officer, time.Now(), candId,
			)
			if err != nil {
				fmt.Println(err)
				continue
			}

		} else {

			anketa.fullname = strings.ToTitle(trimmString(parseStringCell(f, "Лист1", "B4")))
			anketa.birthday = parseDateCell(f, "Лист1", "B5", "02.01.2006")

			robot.employee = parseStringCell(f, "Лист1", "B27")
			robot.terrorist = parseStringCell(f, "Лист1", "B17")
			robot.inn = parseStringCell(f, "Лист1", "B18")
			bnkrpt := parseStringCell(f, "Лист1", "B20")
			bnkrpt2 := parseStringCell(f, "Лист1", "B21")
			bnkrpt3 := parseStringCell(f, "Лист1", "B22")
			robot.bankruptcy = fmt.Sprintf("%s, %s, %s", bnkrpt, bnkrpt2, bnkrpt3)
			robot.mvd = parseStringCell(f, "Лист1", "B23")
			robot.courts = parseStringCell(f, "Лист1", "B24")
			robot.bki = parseStringCell(f, "Лист1", "B25")

			result := db.QueryRow(
				"SELECT id FROM persons WHERE fullname = ? AND birthday = ?",
				anketa.fullname, anketa.birthday,
			)
			err = result.Scan(&candId)
			if err != nil {
				if err == sql.ErrNoRows {
					result, err := stmtShortInsertPerson.Exec(
						anketa.fullname, anketa.birthday, time.Now(), categoryId, regionId, statusId,
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
				_, err := stmtShortUpdatePerson.Exec(
					anketa.fullname, anketa.birthday, time.Now(), categoryId, regionId, statusId, candId,
				)
				if err != nil {
					fmt.Println(err)
					continue
				}
			}

			_, err = stmtInsertRobot.Exec(robot.inn, robot.employee, robot.terrorist, robot.mvd, robot.courts, robot.bankruptcy, robot.bki, time.Now(), candId)
			if err != nil {
				fmt.Println(err)
				continue
			}
		}
	}
}
