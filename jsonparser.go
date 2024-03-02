package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/go-playground/validator/v10"
	_ "github.com/mattn/go-sqlite3"
)

type NameChange struct {
	Reason                   string `json:"reason" validate:"required"`
	FirstNameBeforeChange    string `json:"firstNameBeforeChange" validate:"required"`
	LastNameBeforeChange     string `json:"lastNameBeforeChange" validate:"required"`
	HasNoMidNameBeforeChange bool   `json:"hasNoMidNameBeforeChange" validate:"required"`
	YearOfChange             int    `json:"yearOfChange" validate:"required"`
	NameChangeDocument       string `json:"nameChangeDocument" validate:"required"`
}

type Education struct {
	EducationType   string `json:"educationType" validate:"required"`
	InstitutionName string `json:"institutionName" validate:"required"`
	BeginYear       int    `json:"beginYear" validate:"required"`
	EndYear         int    `json:"endYear" validate:"required"`
	Specialty       string `json:"specialty" validate:"required"`
}

type Experience struct {
	BeginDate                         string `json:"beginDate" validate:"required"`
	EndDate                           string `json:"endDate,omitempty" validate:"required"`
	CurrentJob                        bool   `json:"currentJob,omitempty" validate:"required"`
	Name                              string `json:"name" validate:"required"`
	Address                           string `json:"address" validate:"required"`
	Phone                             string `json:"phone" validate:"required"`
	ActivityType                      string `json:"activityType" validate:"required"`
	Position                          string `json:"position" validate:"required"`
	IsPositionMatchEmploymentContract bool   `json:"isPositionMatchEmploymentContract,omitempty" validate:"required"`
	EmploymentContractPosition        string `json:"employmentContractPosition,omitempty" validate:"required"`
	FireReason                        string `json:"fireReason,omitempty" validate:"required"`
}

type Organization struct {
	View     string `json:"view" validate:"required"`
	Inn      string `json:"inn" validate:"required"`
	OrgType  string `json:"orgType" validate:"required"`
	Name     string `json:"name" validate:"required"`
	Position string `json:"position" validate:"required"`
}

type Person struct {
	PositionName                      string         `json:"positionName" validate:"required"`
	Department                        string         `json:"department" validate:"required"`
	StatusDate                        string         `json:"statusDate" validate:"required"`
	LastName                          string         `json:"lastName" validate:"required"`
	FirstName                         string         `json:"firstName" validate:"required"`
	MidName                           string         `json:"midName" validate:"required"`
	HasNameChanged                    bool           `json:"hasNameChanged" validate:"required"`
	NameWasChanged                    []NameChange   `json:"nameWasChanged" validate:"required"`
	Birthday                          string         `json:"birthday" validate:"required"`
	Birthplace                        string         `json:"birthplace" validate:"required"`
	Citizen                           string         `json:"citizen" validate:"required"`
	HasAdditionalCitizenship          bool           `json:"hasAdditionalCitizenship"`
	AdditionalCitizenship             string         `json:"additionalCitizenship" validate:"required"`
	MaritalStatus                     string         `json:"maritalStatus" validate:"required"`
	RegAddress                        string         `json:"regAddress" validate:"required"`
	ValidAddress                      string         `json:"validAddress" validate:"required"`
	ContactPhone                      string         `json:"contactPhone" validate:"required"`
	HasNoRussianContactPhone          bool           `json:"hasNoRussianContactPhone" validate:"required"`
	Email                             string         `json:"email" validate:"required"`
	HasInn                            bool           `json:"hasInn" validate:"required"`
	Inn                               string         `json:"inn" validate:"required"`
	HasSnils                          bool           `json:"hasSnils" validate:"required"`
	Snils                             string         `json:"snils" validate:"required"`
	PassportSerial                    string         `json:"passportSerial" validate:"required"`
	PassportNumber                    string         `json:"passportNumber" validate:"required"`
	PassportIssueDate                 string         `json:"passportIssueDate" validate:"required"`
	PassportIssuedBy                  string         `json:"passportIssuedBy" validate:"required"`
	Education                         []Education    `json:"education" validate:"required"`
	HasJob                            bool           `json:"hasJob" validate:"required"`
	Experience                        []Experience   `json:"experience" validate:"required"`
	HasPublicOfficeOrganizations      bool           `json:"hasPublicOfficeOrganizations" validate:"required"`
	PublicOfficeOrganizations         []Organization `json:"publicOfficeOrganizations" validate:"required"`
	HasStateOrganizations             bool           `json:"hasStateOrganizations" validate:"required"`
	StateOrganizations                []Organization `json:"stateOrganizations" validate:"required"`
	HasRelatedPersonsOrganizations    bool           `json:"hasRelatedPersonsOrganizations" validate:"required"`
	RelatedPersonsOrganizations       []Organization `json:"relatedPersonsOrganizations" validate:"required"`
	HasMtsRelatedPersonsOrganizations bool           `json:"hasMtsRelatedPersonsOrganizations" validate:"required"`
	MtsRelatedPersonsOrganizations    []Organization `json:"mtsRelatedPersonsOrganizations" validate:"required"`
	HasOrganizations                  bool           `json:"hasOrganizations" validate:"required"`
	Organizations                     []Organization `json:"organizations" validate:"required"`
}

var validate *validator.Validate

func jsonParse(db *sql.DB, jsonPath string, jsonFile string) {
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

	f, err := os.ReadFile(filepath.Join(jsonPath, jsonFile))
	if err != nil {
		log.Println(err)
		return
	}

	var candId int
	var person Person

	err = json.Unmarshal(f, &person)
	if err != nil {
		log.Println(err)
		return
	}

	validate = validator.New(validator.WithRequiredStructEnabled())
	err = validate.Struct(person)
	if err != nil {
		if e, ok := err.(*validator.InvalidValidationError); ok {
			fmt.Println(e)
			return
		}
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
				return
			}
			id, err := ins.LastInsertId()
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
		_, err := stmts["stmtUpdatePerson"].Exec(
			person.parseFullname(), person.parsePrevious(), person.Birthday,
			person.Birthplace, person.Citizen, person.AdditionalCitizenship,
			person.Snils, person.Inn, person.MaritalStatus, person.parseEducation(),
			time.Now(), categoryId, regionId, statusId, candId,
		)
		if err != nil {
			log.Println(err)
			return
		}
	}

	_, err = stmts["stmtInsertStaff"].Exec(person.PositionName, person.Department, candId)
	if err != nil {
		log.Println(err)
		return
	}

	_, err = stmts["stmtInsertDocument"].Exec(
		"Паспорт", person.PassportSerial, person.PassportNumber,
		person.PassportIssueDate, person.PassportIssuedBy, candId,
	)
	if err != nil {
		log.Println(err)
		return
	}

	_, err = stmts["stmtInsertAddress"].Exec("Адрес проживания", person.ValidAddress, candId)
	if err != nil {
		log.Println(err)
		return
	}

	_, err = stmts["stmtInsertAddress"].Exec("Адрес регистрации", person.RegAddress, candId)
	if err != nil {
		log.Println(err)
		return
	}

	_, err = stmts["stmtInsertContacts"].Exec("Телефон", person.ContactPhone, candId)
	if err != nil {
		log.Println(err)
		return
	}

	_, err = stmts["stmtInsertContacts"].Exec("Электронная почта", person.Email, candId)
	if err != nil {
		log.Println(err)
		return
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
