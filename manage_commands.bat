@echo off
setlocal

rem Set the path to manage.py and Python executable
set MANAGE_PY_PATH=.\backend\manage.py
set PYTHON_PATH=.\myenv\Scripts\python.exe
set REACT_FRONTEND_PATH=.\frontend

rem Function to check if virtual environment is activated
:CHECK_VENV
for /F "tokens=2 delims=." %%i in ('%PYTHON_PATH% -c "import sys; print(sys.prefix)"') do (
    if "%%i" == "myenv" (
        echo Virtual environment already activated.
        goto MENU
    )
)
call .\myenv\Scripts\activate

rem Menu for selecting the command to run
:MENU
echo Select a command to run:
echo 1. Make migrations
echo 2. Migrate
echo 3. Run Django server
echo 4. Run React frontend
echo 5. Run Django server and React frontend
echo 6. Concatenate Files
echo 7. Generate Model Diagram
echo 8. Write API_documentation.md
echo 9. Exit

set /p choice="Enter your choice: "

if "%choice%" == "1" goto MAKEMIGRATIONS
if "%choice%" == "2" goto MIGRATE
if "%choice%" == "3" goto RUNSERVER
if "%choice%" == "4" goto RUN_FRONTEND
if "%choice%" == "5" goto RUN_BOTH
if "%choice%" == "6" goto CONCAT_ALL
if "%choice%" == "7" goto GEN_DIAGRAM
if "%choice%" == "8" goto WRITE_API_DOC
if "%choice%" == "9" goto END
echo Invalid choice. Please try again.
goto MENU

:MAKEMIGRATIONS
%PYTHON_PATH% %MANAGE_PY_PATH% makemigrations
goto MENU

:MIGRATIONS
%PYTHON_PATH% %MANAGE_PY_PATH% migrate
goto MENU

:RUNSERVER
start cmd /k "%PYTHON_PATH% %MANAGE_PY_PATH% runserver"
goto MENU

:RUN_FRONTEND
start cmd /k "cd /d %REACT_FRONTEND_PATH% && npm start"
goto MENU

:RUN_BOTH
start cmd /k "%PYTHON_PATH% %MANAGE_PY_PATH% runserver"
start cmd /k "cd /d %REACT_FRONTEND_PATH% && npm start"
goto MENU

:CONCAT_ALL
%PYTHON_PATH% %MANAGE_PY_PATH% concatenate_project
goto MENU

:GEN_DIAGRAM
%PYTHON_PATH% %MANAGE_PY_PATH% generate_model_diagram
goto MENU

:WRITE_API_DOC
%PYTHON_PATH% %MANAGE_PY_PATH% generate_api_docs
goto MENU

:END
endlocal
echo Exiting...
