@echo off

echo --------- Environment being activated ---------

set "BASE=%~dp0\.."
set "PYTHONPATH=%base%;%base%\sources;%PYTHONPATH%"


if exist "%~dp0\..\venv" (goto activate_venv) else (goto activate_portable_embedded_python)

:activate_portable_embedded_python:
echo info - activating portable embedded python
set "path2interpreterdir=%~dp0\..\python"
set "PATH=%~dp0;%path2interpreterdir%;%PATH%"
goto end


:activate_venv:
echo info - activating virtual environnement
set "path2scripts=%~dp0\..\venv\Scripts"
set "PATH=%~dp0;%path2scripts%;%PATH%"
call "%base%\venv\Scripts\activate.bat"
goto end


:end:



