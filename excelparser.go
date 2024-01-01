package main

import (
	"database/sql"
	"fmt"
	"log"
	"path/filepath"
	"regexp"
	"strings"
	"time"

	_ "github.com/mattn/go-sqlite3"
	"github.com/xuri/excelize/v2"
)

type Anketa struct {
	fullname   string
	previous   string
	birthday   time.Time
	birthplace string
	country    string
	snils      string
	inn        string
	education  string
}

type Check struct {
	workplace   string
	cronos      string
	cros        string
	document    string
	debt        string
	bankruptcy  string
	bki         string
	affiliation string
	internet    string
	pfo         bool
	addition    string
	conclusion  int
	officer     string
	deadline    time.Time
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

func excelParse(excelPaths []string, excelFiles []string) {
	db, err := sql.Open("sqlite3", databaseURI)
	if err != nil {
		log.Fatal(err)
		return
	}
	defer db.Close()

	stmtUpdatePerson, err := db.Prepare("UPDATE persons SET fullname = ?, previous = ?, birthday = ?, birthplace = ?, country = ?, snils = ?, inn = ?, education = ?, `update` = ?, category_id = ?, region_id = ?, status_id = ? WHERE id = ?")
	if err != nil {
		log.Fatal(err)
	}
	defer stmtUpdatePerson.Close()

	stmtShortUpdatePerson, err := db.Prepare("UPDATE persons SET fullname = ?, birthday = ?, `update` = ?, category_id = ?, region_id = ?, status_id = ? WHERE id = ?")
	if err != nil {
		log.Fatal(err)
	}
	defer stmtUpdatePerson.Close()

	stmtShortInsertPerson, err := db.Prepare("INSERT INTO persons (fullname, birthday, `create`, category_id, region_id, status_id) VALUES (?, ?, ?, ?, ?, ?)")
	if err != nil {
		log.Fatal(err)
	}
	defer stmtShortInsertPerson.Close()

	stmtInsertPerson, err := db.Prepare("INSERT INTO persons (fullname, previous, birthday, birthplace, country, snils, inn, education, `create`, category_id, region_id, status_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
	if err != nil {
		log.Fatal(err)
	}
	defer stmtInsertPerson.Close()

	stmtInsertCheck, err := db.Prepare("INSERT INTO checks (workplace, cronos, cros, document, debt, bankruptcy, bki, affiliation, internet, pfo, addition, conclusion, officer, deadline, person_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
	if err != nil {
		log.Fatal(err)
	}
	defer stmtInsertCheck.Close()

	stmtInsertRobot, err := db.Prepare("INSERT INTO robots (inn, employee, terrorist, mvd, courts, bankruptcy, bki, deadline, person_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)")
	if err != nil {
		log.Fatal(err)
	}
	defer stmtInsertRobot.Close()

	for idx, file := range excelFiles {
		f, err := excelize.OpenFile(filepath.Join(excelPaths[idx], file))
		if err != nil {
			log.Fatal(err)
		}
		defer f.Close()

		var candId int
		var fio string
		var anketa Anketa
		var check Check
		var robot Robot

		if strings.HasPrefix(file, "Заключение") {
			anketa.fullname, err = f.GetCellValue("Лист1", "C6")
			if err != nil {
				anketa.fullname = err.Error()
			}
			birth, err := f.GetCellValue("Лист1", "C8")
			if err != nil {
				birth = "02.01.2006"
			}
			day, err := time.Parse("02.01.2006", birth)
			if err != nil {
				day = time.Now()
			}
			anketa.birthday = day.Truncate(24 * time.Hour)
			anketa.previous, err = f.GetCellValue("Лист1", "C7")
			if err != nil {
				anketa.previous = err.Error()
			}

			if f.SheetCount > 1 {
				fio, err = f.GetCellValue("Лист2", "K1")
				if err != nil {
					log.Fatal(err)
				}

				if fio == "ФИО" {
					anketa.fullname, err = f.GetCellValue("Лист2", "K3")
					if err != nil {
						anketa.fullname = err.Error()
					}
					anketa.previous, err = f.GetCellValue("Лист2", "S3")
					if err != nil {
						anketa.previous = err.Error()
					}
					birth, err := f.GetCellValue("Лист2", "L3")
					if err != nil {
						birth = "02.01.2006"
					}
					day, err := time.Parse("02.01.2006", birth)
					if err != nil {
						day = time.Now()
					}
					anketa.birthday = day.Truncate(24 * time.Hour)
					anketa.birthplace, err = f.GetCellValue("Лист2", "M3")
					if err != nil {
						anketa.birthplace = err.Error()
					}
					anketa.country, err = f.GetCellValue("Лист2", "T3")
					if err != nil {
						anketa.country = err.Error()
					}
					anketa.snils, err = f.GetCellValue("Лист2", "U3")
					if err != nil {
						anketa.snils = err.Error()
					}
					anketa.inn, err = f.GetCellValue("Лист2", "V3")
					if err != nil {
						anketa.inn = err.Error()
					}
					anketa.education, err = f.GetCellValue("Лист2", "W3")
					if err != nil {
						anketa.education = err.Error()
					}
				}
			}

			wp1, err := f.GetCellValue("Лист1", "D11")
			if err != nil {
				wp1 = ""
			}
			wp2, err := f.GetCellValue("Лист1", "D12")
			if err != nil {
				wp2 = ""
			}
			wp3, err := f.GetCellValue("Лист1", "D13")
			if err != nil {
				wp3 = ""
			}
			check.workplace = fmt.Sprintf("%s; %s; %s", wp1, wp2, wp3)
			check.cronos, err = f.GetCellValue("Лист1", "C14")
			if err != nil {
				check.cronos = err.Error()
			}
			check.cros, err = f.GetCellValue("Лист1", "C16")
			if err != nil {
				check.cros = err.Error()
			}
			check.document, err = f.GetCellValue("Лист1", "C17")
			if err != nil {
				check.document = err.Error()
			}
			check.debt, err = f.GetCellValue("Лист1", "C18")
			if err != nil {
				check.debt = err.Error()
			}
			check.bankruptcy, err = f.GetCellValue("Лист1", "C19")
			if err != nil {
				check.bankruptcy = err.Error()
			}
			check.bki, err = f.GetCellValue("Лист1", "C20")
			if err != nil {
				check.bki = err.Error()
			}
			check.affiliation, err = f.GetCellValue("Лист1", "C21")
			if err != nil {
				check.affiliation = err.Error()
			}
			check.internet, err = f.GetCellValue("Лист1", "C22")
			if err != nil {
				check.internet = err.Error()
			}
			decision, err := f.GetCellValue("Лист1", "C23")
			if err != nil {
				decision = "Согласовано"
			}
			check.conclusion = getConclusionId(decision)
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
			check.officer, err = f.GetCellValue("Лист1", "C25")
			if err != nil {
				check.officer = err.Error()
			}
			check.addition, err = f.GetCellValue("Лист1", "C28")
			if err != nil {
				check.addition = err.Error()
			}

			result := db.QueryRow(
				"SELECT id FROM persons WHERE fullname = ? AND birthday = ?",
				anketa.fullname, anketa.birthday,
			)
			err = result.Scan(&candId)
			if err != nil && err != sql.ErrNoRows {
				candId = 0
			}

			if err == sql.ErrNoRows {
				result, err := stmtInsertPerson.Exec(
					anketa.fullname, anketa.previous, anketa.birthday, anketa.birthplace, anketa.country, anketa.snils, anketa.inn, anketa.education, time.Now().Truncate(24*time.Hour), categoryId, regionId, statusId,
				)
				if err != nil {
					log.Fatal(err)
				}
				id, err := result.LastInsertId()
				if err != nil {
					log.Fatal(err)
				}
				candId = int(id)

			} else {
				if fio == "" {
					_, err := stmtUpdatePerson.Exec(
						anketa.fullname, anketa.previous, anketa.birthday, anketa.birthplace, anketa.country, anketa.snils, anketa.inn, anketa.education, time.Now().Truncate(24*time.Hour), categoryId, regionId, statusId, candId,
					)
					if err != nil {
						log.Fatal(err)
					}
				} else {
					_, err := stmtShortUpdatePerson.Exec(
						anketa.fullname, anketa.birthday, time.Now(), categoryId, regionId, statusId, candId,
					)
					if err != nil {
						log.Fatal(err)
					}
				}

			}

			_, err = stmtInsertCheck.Exec(
				check.workplace, check.cronos, check.cros, check.document, check.debt, check.bankruptcy, check.bki, check.affiliation, check.internet, check.pfo, check.addition, check.conclusion, check.officer, time.Now().Truncate(24*time.Hour), candId,
			)
			if err != nil {
				log.Fatal(err)
			}

		} else {
			name, err := f.GetCellValue("Лист1", "B4")
			if err != nil {
				anketa.fullname = err.Error()
			}
			trimmed := strings.TrimSpace(name)
			re := regexp.MustCompile(`\s+`)
			anketa.fullname = re.ReplaceAllString(trimmed, " ")

			birth, err := f.GetCellValue("Лист1", "B5")
			if err != nil {
				birth = "02.01.2006"
			}
			day, err := time.Parse("02.01.2006", birth)
			if err != nil {
				day = time.Now()
			}
			anketa.birthday = day.Truncate(24 * time.Hour)
			robot.employee, err = f.GetCellValue("Лист1", "B27")
			if err != nil {
				robot.employee = err.Error()
			}
			robot.terrorist, err = f.GetCellValue("Лист1", "B17")
			if err != nil {
				robot.terrorist = err.Error()
			}
			robot.inn, err = f.GetCellValue("Лист1", "B18")
			if err != nil {
				robot.inn = err.Error()
			}
			bankruptcy1, err := f.GetCellValue("Лист1", "B20")
			if err != nil {
				robot.bankruptcy = err.Error()
			}
			bankruptcy2, err := f.GetCellValue("Лист1", "B21")
			if err != nil {
				robot.bankruptcy = err.Error()
			}
			bankruptcy3, err := f.GetCellValue("Лист1", "B22")
			if err != nil {
				robot.bankruptcy = err.Error()
			}
			robot.bankruptcy = fmt.Sprintf("%s, %s, %s", bankruptcy1, bankruptcy2, bankruptcy3)
			robot.mvd, err = f.GetCellValue("Лист1", "B23")
			if err != nil {
				robot.mvd = err.Error()
			}
			robot.mvd, err = f.GetCellValue("Лист1", "B23")
			if err != nil {
				robot.mvd = err.Error()
			}
			robot.courts, err = f.GetCellValue("Лист1", "B24")
			if err != nil {
				robot.courts = err.Error()
			}
			robot.bki, err = f.GetCellValue("Лист1", "B25")
			if err != nil {
				check.bki = err.Error()
			}

			result := db.QueryRow(
				"SELECT id FROM persons WHERE fullname = ? AND birthday = ?",
				anketa.fullname, anketa.birthday,
			)
			err = result.Scan(&candId)
			if err != nil && err != sql.ErrNoRows {
				candId = 0
			}
			if err == sql.ErrNoRows {
				result, err := stmtShortInsertPerson.Exec(
					anketa.fullname, anketa.birthday, time.Now().Truncate(24*time.Hour), categoryId, regionId, statusId,
				)
				if err != nil {
					log.Fatal(err)
				}
				id, err := result.LastInsertId()
				if err != nil {
					log.Fatal(err)
				}
				candId = int(id)

			} else {
				_, err := stmtShortUpdatePerson.Exec(
					anketa.fullname, anketa.birthday, time.Now(), categoryId, regionId, statusId, candId,
				)
				if err != nil {
					log.Fatal(err)
				}
			}

			_, err = stmtInsertRobot.Exec(robot.inn, robot.employee, robot.terrorist, robot.mvd, robot.courts, robot.bankruptcy, robot.bki, time.Now().Truncate(24*time.Hour), candId)
			if err != nil {
				log.Fatal(err)
			}
		}
	}
}
