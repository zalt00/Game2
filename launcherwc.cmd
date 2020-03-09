@call "%~dp0\commands\activate.cmd"
set "pythonpath=%pythonpath%;%~dp0\sources"
@start pythonw main.py
