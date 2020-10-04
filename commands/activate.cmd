@echo off

echo --------- Environment being activated ---------

set "path2scripts=%~dp0\..\venv\Scripts"
set "BASE=%~dp0\.."
set "PATH=%~dp0;%path2scripts%;%PATH%"
set "PYTHONPATH=%base%;%base%\sources;%PYTHONPATH%"
call "%base%\venv\Scripts\activate.bat"
