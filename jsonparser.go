package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"io"
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

func jsonParse(jsonPaths []string) {
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

	stmtUpdatePerson, err := db.Prepare("UPDATE persons SET fullname = ?, previous = ?, birthday = ?, birthplace = ?, country = ?, ext_country = ?, snils = ?, inn = ?, marital = ?, education = ?, create = ?, category_id = ?, region_id = ?, status_id = ? WHERE id = ?")
	if err != nil {
		log.Fatal(err)
	}
	defer stmtUpdatePerson.Close()

	stmtInsertPerson, err := db.Prepare("INSERT INTO persons (fullname, previous, birthday, birthplace, country, snils, inn, education, update, category_id, region_id, status_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
	if err != nil {
		log.Fatal(err)
	}
	defer stmtInsertPerson.Close()

	stmtInsertStaff, err := db.Prepare("INSERT INTO staffs (position, department, person_id) VALUES (?, ?, ?)")
	if err != nil {
		log.Fatal(err)
	}
	defer stmtInsertStaff.Close()

	stmtInsertDocument, err := db.Prepare("INSERT INTO documents (view, series, number, issue, agency, person_id) VALUES (?, ?, ?, ?, ?, ?)")
	if err != nil {
		log.Fatal(err)
	}
	defer stmtInsertDocument.Close()

	stmtInsertAddress, err := db.Prepare("INSERT INTO addresses (view, address, person_id) VALUES (?, ?, ?)")
	if err != nil {
		log.Fatal(err)
	}
	defer stmtInsertAddress.Close()

	stmtInsertContacts, err := db.Prepare("INSERT INTO contacts (view, contact, person_id) VALUES (?, ?, ?, ?)")
	if err != nil {
		log.Fatal(err)
	}
	defer stmtInsertContacts.Close()

	stmtInsertAffiliation, err := db.Prepare("INSERT INTO affiliations (view, name, inn, position, person_id) VALUES (?, ?, ?, ?, ?)")
	if err != nil {
		log.Fatal(err)
	}
	defer stmtInsertAffiliation.Close()

	stmtInsertWorkplace, err := db.Prepare("INSERT INTO workplaces (start_date, end_date, position, organization, reason, person_id) VALUES (?, ?, ?, ?, ?, ?)")
	if err != nil {
		log.Fatal(err)
	}
	defer stmtInsertWorkplace.Close()

	for _, path := range jsonPaths {
		f, err := os.Open(path)
		if err != nil {
			log.Fatal(err)
		}
		defer f.Close()

		var candId int
		var person Person

		jsonData, err := io.ReadAll(f)
		if err != nil {
			log.Fatal(err)
			return
		}

		err = json.Unmarshal(jsonData, &person)
		if err != nil {
			log.Fatal(err)
			return
		}

		result := stmtSelectPerson.QueryRow(resume.fullname, resume.birthday)
		err = result.Scan(&candId)
		if err != nil {
			log.Fatal(err)
		}

		if candId == 0 {
			ins, err := stmtInsertPerson.Exec(
				person.parseFullname(), person.parsePrevious(), person.parseBirthday(), person.Birthplace, person.Citizen, person.AdditionalCitizenship, person.Snils, person.Inn, person.MaritalStatus, person.parseEducation(), time.Now().Truncate(24*time.Hour), categoryId, regionId, statusId,
			)
			if err != nil {
				log.Fatal(err)
			}
			insId, err := ins.LastInsertId()
			if err != nil {
				log.Fatal(err)
			}
			candId = int(insId)

		} else {
			_, err := stmtUpdatePerson.Exec(
				person.parseFullname(), person.parsePrevious(), person.parseBirthday(), person.Birthplace, person.Citizen, person.AdditionalCitizenship, person.Snils, person.Inn, person.MaritalStatus, person.parseEducation(), time.Now().Truncate(24*time.Hour), categoryId, regionId, statusId, candId,
			)
			if err != nil {
				log.Fatal(err)
			}
		}

		_, err = stmtInsertStaff.Exec(person.PositionName, person.Department, candId)
		if err != nil {
			log.Fatal(err)
		}

		_, err = stmtInsertDocument.Exec(person.PassportSerial, person.PassportNumber, person.PassportIssueDate, person.PassportIssuedBy, person.PassportIssuedBy, candId)
		if err != nil {
			log.Fatal(err)
		}

		_, err = stmtInsertAddress.Exec("Адрес проживания", person.ValidAddress, candId)
		if err != nil {
			log.Fatal(err)
		}

		_, err = stmtInsertAddress.Exec("Адрес регистрации", person.RegAddress, candId)
		if err != nil {
			log.Fatal(err)
		}

		_, err = stmtInsertContacts.Exec("Телефон", person.ContactPhone, candId)
		if err != nil {
			log.Fatal(err)
		}

		_, err = stmtInsertContacts.Exec("Электронная почта", person.Email, candId)
		if err != nil {
			log.Fatal(err)
		}

		for _, item := range person.parseAffilation() {
			_, err = stmtInsertAffiliation.Exec(item.View, item.Inn, item.Position, item.Name, candId)
			if err != nil {
				log.Fatal(err)
			}
		}

		for _, item := range person.parseWorkplace() {
			_, err = stmtInsertWorkplace.Exec(
				item.BeginDate, item.EndDate, item.Name, item.Position, item.FireReason, candId)
			if err != nil {
				log.Fatal(err)
			}

		}
	}
}

func (person Person) parseFullname() string {
	return fmt.Sprintf("%s %s %s", person.LastName, person.FirstName, person.MidName)
}

func (person Person) parseBirthday() time.Time {
	t, err := time.Parse("2006-01-02", person.Birthday)
	if err != nil {
		log.Fatal(err)
	}
	return t
}

func (person Person) parsePrevious() string {
	var previous []string
	if person.HasNameChanged {
		for _, item := range person.NameWasChanged {
			previous = append(previous, fmt.Sprintf("%s - %s %d %s, %s",
				item.FirstNameBeforeChange, item.LastNameBeforeChange, item.YearOfChange, item.NameChangeDocument, item.Reason))
		}
	}
	return strings.Join(previous, "")
}

func (person Person) parseEducation() string {
	var education []string
	if len(person.Education) > 0 {
		for _, item := range person.Education {
			education = append(education, fmt.Sprintf("%s %s %d %d", item.EducationType, item.InstitutionName, item.BeginYear, item.EndYear))
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
				View:     "Связанные лица работают в госудраственных организациях",
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
