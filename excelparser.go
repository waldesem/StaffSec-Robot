package main

import (
	"database/sql"
	"fmt"
	"log"
	"strings"
	"time"

	_ "github.com/mattn/go-sqlite3"
	"github.com/xuri/excelize/v2"
)

const (
	categoryId = 1
	statusId   = 9
	regionId   = 1
)

var resume struct {
	fullname   string
	previous   string
	birthday   time.Time
	birthplace string
	country    string
	snils      string
	inn        string
	education  string
}

var check struct {
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
	conclusion  string
	officer     string
	deadline    time.Time
	idCandidate int
}

var robot struct {
	inn         string
	employee    string
	terrorist   string
	mvd         string
	courts      string
	bankruptcy  string
	bki         string
	idCandidate int
}

func excelParse(excelPaths []string) {
	db, err := sql.Open("sqlite3", databaseURI)
	if err != nil {
		log.Fatal(err)
		return
	}
	defer db.Close()

	stmtSelectPerson, err := db.Prepare("SELECT id FROM persons WHERE fullname = ? AND birthday = ?")
	if err != nil {
		log.Fatal(err)
	}
	defer stmtSelectPerson.Close()

	stmtUpdatePerson, err := db.Prepare("UPDATE persons SET update = ? WHERE id = ?")
	if err != nil {
		log.Fatal(err)
	}
	defer stmtUpdatePerson.Close()

	stmtInsertPerson, err := db.Prepare("INSERT INTO persons (fullname, birthday, create, category_id, region_id, status_id) VALUES (?, ?, ?, ?, ?, ?)")
	if err != nil {
		log.Fatal(err)
	}
	defer stmtInsertPerson.Close()

	stmtInsertCheck, err := db.Prepare("INSERT INTO checks (person_id, conclusion_id, deadline) VALUES (?, ?, ?)")
	if err != nil {
		log.Fatal(err)
	}
	defer stmtInsertCheck.Close()

	stmtInsertRobot, err := db.Prepare("INSERT INTO robots (person_id) VALUES (?)")
	if err != nil {
		log.Fatal(err)
	}
	defer stmtInsertRobot.Close()

	for _, path := range excelPaths {
		f, err := excelize.OpenFile(path)
		if err != nil {
			log.Fatal(err)
		}
		defer f.Close()

		var candId int

		if strings.hasPrefix(path, "Заключение") {
			if f.SheetCount > 1 {
				fio, err := f.GetCellValue("Лист2", "K1")
				if err != nil {
					log.Fatal(err)
				}

				if fio == "ФИО" {
					resume.fullname, err = f.GetCellValue("Лист2", "K2")
					if err != nil {
						resume.fullname = err.Error()
					}
					resume.previous, err = f.GetCellValue("Лист2", "K3")
					if err != nil {
						resume.previous = err.Error()
					}
					resume.birthday, err = f.GetCellValue("Лист2", "L3")
					if err != nil {
						resume.birthday = err.Error()
					}
					resume.birthplace, err = f.GetCellValue("Лист2", "M3")
					if err != nil {
						resume.birthplace = err.Error()
					}
					resume.country, err = f.GetCellValue("Лист2", "T3")
					if err != nil {
						resume.country = err.Error()
					}
					resume.snils, err = f.GetCellValue("Лист2", "U3")
					if err != nil {
						resume.snils = err.Error()
					}
					resume.inn, err = f.GetCellValue("Лист2", "V3")
					if err != nil {
						resume.inn = err.Error()
					}
					resume.education, err = f.GetCellValue("Лист2", "W3")
					if err != nil {
						resume.education = err.Error()
					}
				}
			}

			resume.fullname, err = f.GetCellValue("Лист1", "C6")
			if err != nil {
				resume.fullname = err.Error()
			}
			resume.birthday, err = f.GetCellValue("Лист1", "C8")
			if err != nil {
				resume.birthday = err.Error()
			}
			resume.previous, err = f.GetCellValue("Лист1", "C9")
			if err != nil {
				resume.previous = err.Error()
			}
			resume.inn, err = f.GetCellValue("Лист1", "C10")
			if err != nil {
				resume.inn = err.Error()
			}
			check.workplace, err = f.GetCellValue("Лист1", "C11")
			if err != nil {
				check.workplace = err.Error()
			}
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
			check.conclusion, err = f.GetCellValue("Лист1", "C23")
			if err != nil {
				check.conclusion = err.Error()
			}
			check.deadline, err = f.GetCellValue("Лист1", "C24")
			if err != nil {
				check.deadline = err.Error()
			}
			poligraf, err := f.GetCellValue("Лист1", "C26")
			if err != nil {
				poligraf = "не назначалось"
			}
			if strings.ToLower(poligraf) == "назначено" || poligraf == "назначено на испытательном сроке" {
				check.pfo = true
			} else {
				check.pfo = false
			}
			check.officer, err = f.GetCellValue("Лист1", "C25")
			if err != nil {
				check.officer = err.Error()
			}

		} else {
			resume.fullname, err = f.GetCellValue("Лист1", "B4")
			if err != nil {
				resume.fullname = err.Error()
			}
			resume.birthday, err = f.GetCellValue("Лист1", "L3")
			if err != nil {
				resume.birthday = err.Error()
			}
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
			robot.courts, err = f.GetCellValue("Лист1", "B24")
			if err != nil {
				robot.courts = err.Error()
			}
			robot.bki, err = f.GetCellValue("Лист1", "B25")
			if err != nil {
				check.bki = err.Error()
			}
		}

		person := stmtSelectPerson.QueryRow(resume.fullname, resume.birthday)
		err = person.Scan(&candId)
		if err != nil {
			log.Fatal(err)
		}

		if candId == 0 {
			ins, err := stmtInsertPerson.Exec(resume.fullname, resume.birthday)
			if err != nil {
				log.Fatal(err)
			}
			insId, err := ins.LastInsertId()
			if err != nil {
				log.Fatal(err)
			}
			candId = int(insId)

		} else {
			_, err := stmtUpdatePerson.Exec(resume.birthday, candId)
			if err != nil {
				log.Fatal(err)
			}
		}

		_, err = stmtInsertCheck.Exec(
			check.bankruptcy, check.bki, check.affiliation, check.internet, check.conclusion, check.deadline, check.pfo, check.officer, candId,
		)
		if err != nil {
			log.Fatal(err)
		}

		_, err = stmtInsertRobot.Exec(robot.employee, robot.terrorist, robot.inn, robot.bankruptcy, robot.mvd, robot.courts, robot.bki, candId)
		if err != nil {
			log.Fatal(err)
		}
	}
}
