package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"strings"
	"time"

	_ "github.com/mattn/go-sqlite3"
)

type NameChange struct {
	Reason                   string `json:"reason"`
	FirstNameBeforeChange    string `json:"firstNameBeforeChange"`
	LastNameBeforeChange     string `json:"lastNameBeforeChange"`
	HasNoMidNameBeforeChange bool   `json:"hasNoMidNameBeforeChange"`
	YearOfChange             int    `json:"yearOfChange"`
	NameChangeDocument       string `json:"nameChangeDocument"`
}

type Education struct {
	EducationType   string `json:"educationType"`
	InstitutionName string `json:"institutionName"`
	BeginYear       int    `json:"beginYear"`
	EndYear         int    `json:"endYear"`
	Specialty       string `json:"specialty"`
}

type Experience struct {
	BeginDate                         string `json:"beginDate"`
	EndDate                           string `json:"endDate,omitempty"`
	CurrentJob                        bool   `json:"currentJob,omitempty"`
	Name                              string `json:"name"`
	Address                           string `json:"address"`
	Phone                             string `json:"phone"`
	ActivityType                      string `json:"activityType"`
	Position                          string `json:"position"`
	IsPositionMatchEmploymentContract bool   `json:"isPositionMatchEmploymentContract,omitempty"`
	EmploymentContractPosition        string `json:"employmentContractPosition,omitempty"`
	FireReason                        string `json:"fireReason,omitempty"`
}

type Organization struct {
	View     string `json:"view"`
	Inn      string `json:"inn"`
	OrgType  string `json:"orgType"`
	Name     string `json:"name"`
	Position string `json:"position"`
}

type Person struct {
	PositionName                      string         `json:"positionName"`
	Department                        string         `json:"department"`
	StatusDate                        string         `json:"statusDate"`
	LastName                          string         `json:"lastName"`
	FirstName                         string         `json:"firstName"`
	MidName                           string         `json:"midName"`
	HasNameChanged                    bool           `json:"hasNameChanged"`
	NameWasChanged                    []NameChange   `json:"nameWasChanged"`
	Birthday                          string         `json:"birthday"`
	Birthplace                        string         `json:"birthplace"`
	Citizen                           string         `json:"citizen"`
	HasAdditionalCitizenship          bool           `json:"hasAdditionalCitizenship"`
	AdditionalCitizenship             string         `json:"additionalCitizenship"`
	MaritalStatus                     string         `json:"maritalStatus"`
	RegAddress                        string         `json:"regAddress"`
	ValidAddress                      string         `json:"validAddress"`
	ContactPhone                      string         `json:"contactPhone"`
	HasNoRussianContactPhone          bool           `json:"hasNoRussianContactPhone"`
	Email                             string         `json:"email"`
	HasInn                            bool           `json:"hasInn"`
	Inn                               string         `json:"inn"`
	HasSnils                          bool           `json:"hasSnils"`
	Snils                             string         `json:"snils"`
	PassportSerial                    string         `json:"passportSerial"`
	PassportNumber                    string         `json:"passportNumber"`
	PassportIssueDate                 string         `json:"passportIssueDate"`
	PassportIssuedBy                  string         `json:"passportIssuedBy"`
	Education                         []Education    `json:"education"`
	HasJob                            bool           `json:"hasJob"`
	Experience                        []Experience   `json:"experience"`
	HasPublicOfficeOrganizations      bool           `json:"hasPublicOfficeOrganizations"`
	PublicOfficeOrganizations         []Organization `json:"publicOfficeOrganizations"`
	HasStateOrganizations             bool           `json:"hasStateOrganizations"`
	StateOrganizations                []Organization `json:"stateOrganizations"`
	HasRelatedPersonsOrganizations    bool           `json:"hasRelatedPersonsOrganizations"`
	RelatedPersonsOrganizations       []Organization `json:"relatedPersonsOrganizations"`
	HasMtsRelatedPersonsOrganizations bool           `json:"hasMtsRelatedPersonsOrganizations"`
	MtsRelatedPersonsOrganizations    []Organization `json:"mtsRelatedPersonsOrganizations"`
	HasOrganizations                  bool           `json:"hasOrganizations"`
	Organizations                     []Organization `json:"organizations"`
}

func jsonParse(db *sql.DB, jsonPaths *[]string) int {
	queries := map[string]string{
		"stmtUpdatePerson":      "UPDATE persons SET fullname = ?, previous = ?, birthday = ?, birthplace = ?, country = ?, ext_country = ?, snils = ?, inn = ?, marital = ?, education = ?, updated = ?, category_id = ?, region_id = ?, status_id = ? WHERE id = ?",
		"stmtInsertPerson":      "INSERT INTO persons (fullname, previous, birthday, birthplace, country, ext_country, snils, inn, marital, education, created, category_id, region_id, status_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
		"stmtInsertStaff":       "INSERT INTO staffs (position, department, person_id) VALUES (?, ?, ?)",
		"stmtInsertDocument":    "INSERT INTO documents (view, series, number, issue, agency, person_id) VALUES (?, ?, ?, ?, ?, ?)",
		"stmtInsertAddress":     "INSERT INTO addresses (view, address, person_id) VALUES (?, ?, ?)",
		"stmtInsertContacts":    "INSERT INTO contacts (view, contact, person_id) VALUES (?, ?, ?)",
		"stmtInsertAffiliation": "INSERT INTO affilations (view, name, inn, position, deadline, person_id) VALUES (?, ?, ?, ?, ?, ?)",
		"stmtInsertWorkplace":   "INSERT INTO workplaces (start_date, end_date, workplace, address, position, reason, person_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
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

	for _, path := range *jsonPaths {
		f, err := os.ReadFile(path)
		if err != nil {
			log.Println(err)
			continue
		}

		var candId int
		var person Person

		err = json.Unmarshal(f, &person)
		if err != nil {
			log.Println(err)
			continue
		}

		result := db.QueryRow(
			"SELECT id FROM persons WHERE fullname = ? AND birthday = ?",
			person.parseFullname(), person.Birthday,
		)
		err = result.Scan(&candId)
		if err != nil {
			if err == sql.ErrNoRows {
				ins, err := stmts["stmtInsertPerson"].Exec(
					person.parseFullname(), person.parsePrevious(), person.Birthday,
					person.Birthplace, person.Citizen, person.AdditionalCitizenship,
					person.Snils, person.Inn, person.MaritalStatus,
					person.parseEducation(), time.Now(), categoryId, regionId, statusId,
				)
				if err != nil {
					log.Println(err)
					continue
				}
				id, err := ins.LastInsertId()
				if err != nil {
					log.Println(err)
					continue
				}
				candId = int(id)

			} else {
				log.Println(err)
				continue
			}

		} else {
			_, err := stmts["stmtUpdatePerson"].Exec(
				person.parseFullname(), person.parsePrevious(), person.Birthday,
				person.Birthplace, person.Citizen, person.AdditionalCitizenship,
				person.Snils, person.Inn, person.MaritalStatus, person.parseEducation(),
				time.Now(), categoryId, regionId, statusId, candId,
			)
			if err != nil {
				log.Println(err)
				continue
			}
		}

		_, err = stmts["stmtInsertStaff"].Exec(person.PositionName, person.Department, candId)
		if err != nil {
			log.Println(err)
			continue
		}

		_, err = stmts["stmtInsertDocument"].Exec(
			"Паспорт", person.PassportSerial, person.PassportNumber,
			person.PassportIssueDate, person.PassportIssuedBy, candId,
		)
		if err != nil {
			log.Println(err)
			continue
		}

		_, err = stmts["stmtInsertAddress"].Exec("Адрес проживания", person.ValidAddress, candId)
		if err != nil {
			log.Println(err)
			continue
		}

		_, err = stmts["stmtInsertAddress"].Exec("Адрес регистрации", person.RegAddress, candId)
		if err != nil {
			log.Println(err)
			continue
		}

		_, err = stmts["stmtInsertContacts"].Exec("Телефон", person.ContactPhone, candId)
		if err != nil {
			log.Println(err)
			continue
		}

		_, err = stmts["stmtInsertContacts"].Exec("Электронная почта", person.Email, candId)
		if err != nil {
			log.Println(err)
			continue
		}

		for _, item := range person.parseAffilation() {
			_, err = stmts["stmtInsertAffiliation"].Exec(
				item.View, item.Name, item.Inn, item.Position, time.Now(), candId,
			)
			if err != nil {
				log.Println(err)
				continue
			}
		}

		for _, item := range person.parseWorkplace() {
			_, err = stmts["stmtInsertWorkplace"].Exec(
				item.BeginDate, item.EndDate, item.Name, item.Address,
				item.Position, item.FireReason, candId,
			)
			if err != nil {
				log.Println(err)
				continue
			}
		}
	}
	return len(*jsonPaths)
}

func (person Person) parseFullname() string {
	name := fmt.Sprintf("%s %s %s", person.LastName, person.FirstName, person.MidName)
	return strings.ToTitle(strings.Join(strings.Fields(name), " "))
}

func (person Person) parsePrevious() string {
	var previous []string
	if person.HasNameChanged {
		for _, item := range person.NameWasChanged {
			previous = append(previous, fmt.Sprintf("%s, %s: %d %s, %s;",
				item.FirstNameBeforeChange, item.LastNameBeforeChange,
				item.YearOfChange, item.NameChangeDocument, item.Reason,
			))
		}
	}
	return strings.Join(previous, "")
}

func (person Person) parseEducation() string {
	var education []string
	if len(person.Education) > 0 {
		for _, item := range person.Education {
			education = append(education, fmt.Sprintf("%s, %s, %d, %d",
				item.EducationType, item.InstitutionName, item.BeginYear, item.EndYear))
		}
	}
	return strings.Join(education, "")
}

func (person Person) parseWorkplace() []Experience {
	var expirience []Experience
	if len(person.Experience) > 0 {
		for _, item := range person.Experience {
			expirience = append(expirience, Experience{
				BeginDate:  item.BeginDate,
				EndDate:    item.EndDate,
				Name:       item.Name,
				Address:    item.Address,
				Position:   item.Position,
				FireReason: item.FireReason,
			})
		}
	}
	return expirience
}

func (person Person) parseAffilation() []Organization {
	var affilation []Organization
	if person.HasPublicOfficeOrganizations {
		for _, item := range person.PublicOfficeOrganizations {
			affilation = append(affilation, Organization{
				View:     "Являлся государственным или муниципальным служащим",
				Name:     item.Name,
				Position: item.Position,
			})
		}
	}
	if person.HasStateOrganizations {
		for _, item := range person.StateOrganizations {
			affilation = append(affilation, Organization{
				View:     "Являлся государственным должностным лицом",
				Name:     item.Name,
				Position: item.Position,
			})
		}
	}
	if person.HasRelatedPersonsOrganizations {
		for _, item := range person.RelatedPersonsOrganizations {
			affilation = append(affilation, Organization{
				View:     "Связанные лица работают в государственных организациях",
				Name:     item.Name,
				Position: item.Position,
				Inn:      item.Inn,
			})
		}
	}
	if person.HasOrganizations {
		for _, item := range person.Organizations {
			affilation = append(affilation, Organization{
				View:     "Участвует в деятельности коммерческих организаций",
				Name:     item.Name,
				Position: item.Position,
				Inn:      item.Inn,
			})
		}
	}
	return affilation
}
