cd ..
cd src
pyinstaller --onefile -w main.py
move main.spec build
move dist\main.exe ..\resources
rmdir /s /q build
rmdir /s /q dist