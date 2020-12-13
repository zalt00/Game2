pyinstaller .\main.py -F -p .\sources\ -p .\data\ --distpath .\ -w --clean
python "%~dp0\copy_chipmunk.py"
