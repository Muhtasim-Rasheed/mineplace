REM PyInstaller build script (name: mineplace)
python -m pyinstaller --onefile --add-data "assets;assets" main.py --name mineplace.exe --noconsole REM For Windows

REM Remove useless files
REM rm -rf build mineplace.exe.spec
REM Do it the Windows way
rmdir /s /q build
del mineplace.exe.spec
