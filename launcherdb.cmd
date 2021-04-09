@call "%~dp0\commands\activate.cmd"
@echo info - launching main program in debug mode
@call python sources\main.py --debug
pause
