@call "%~dp0\commands\activate.cmd"
set "pythonpath=%pythonpath%;%~dp0\sources"
@call python main.py
pause
