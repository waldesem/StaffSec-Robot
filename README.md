# Staff-Robot

Staff-Robot an automated bot that parse excel and json files in current directory and insert data to database.

## How to use

Clone the repository, install Golang and dependencies from `go.mod`.
Build binary on linux:
- `go build -o parser` for linux
- `GOOS=windows GOARCH=386 go build -o parser.exe .` for windows x86
- `GOOS=windows GOARCH=amd64 go build -o parser.exe .` for windows x64
Run binary:
- `./parser` for linux
- `./parser.exe` for windows

