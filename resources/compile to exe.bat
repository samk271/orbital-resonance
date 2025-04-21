cd ..
cd src
pyinstaller --onefile -w main.py
move main.spec build
move dist\main.exe ..
rmdir /s /q build
rmdir /s /q dist