cd ..
cd src
pyinstaller --onefile --strip --upx-dir ..\resources\upx-5.0.0-win64 main.py
move main.spec build
move dist\main.exe ..
rmdir /s /q build
rmdir /s /q dist