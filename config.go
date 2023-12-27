package main

import (
	"os"
)

type Config struct {
	DatabaseURI string
	BasePath    string
	WorkDir     string
	ArchiveDir  string
	ArchiveDir2 string
	MainFile    string
	InfoFile    string
}

var ConfigInstance = Config{
	DatabaseURI: "sqlite:///personal.db",
	BasePath:    os.Getenv("BASE_PATH"),
	WorkDir:     os.Getenv("WORK_DIR"),
	ArchiveDir:  os.Getenv("ARCHIVE_DIR"),
	ArchiveDir2: os.Getenv("ARCHIVE_DIR_2"),
	MainFile:    os.Getenv("MAIN_FILE"),
	InfoFile:    os.Getenv("INFO_FILE"),
}

func init() {
	if ConfigInstance.BasePath == "" {
		ConfigInstance.BasePath = os.Getenv("BASE_PATH")
	}
	if ConfigInstance.WorkDir == "" {
		ConfigInstance.WorkDir = os.Getenv("WORK_DIR")
	}
	if ConfigInstance.ArchiveDir == "" {
		ConfigInstance.ArchiveDir = os.Getenv("ARCHIVE_DIR")
	}
	if ConfigInstance.ArchiveDir2 == "" {
		ConfigInstance.ArchiveDir2 = os.Getenv("ARCHIVE_DIR_2")
	}
	if ConfigInstance.MainFile == "" {
		ConfigInstance.MainFile = os.Getenv("MAIN_FILE")
	}
	if ConfigInstance.InfoFile == "" {
		ConfigInstance.InfoFile = os.Getenv("INFO_FILE")
	}
}

/*
   BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
   WORK_DIR = os.path.join(BASE_PATH, 'Кандидаты')
   ARCHIVE_DIR = os.path.join(BASE_PATH, 'Персонал')
   ARCHIVE_DIR_2 = os.path.join(ARCHIVE_DIR, 'Персонал-2')
   MAIN_FILE = os.path.join(WORK_DIR, 'Кандидаты.xlsm')
   INFO_FILE = os.path.join(WORK_DIR, 'Запросы по работникам.xlsx')
   DATABASE_URI = 'sqlite:///' + os.path.join(BASE_PATH, 'personal.db')
*/
