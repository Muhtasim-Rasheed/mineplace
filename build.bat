python -m pyinstaller --onefile --add-data "assets;assets" main.py --name mineplace.exe --noconsole

rmdir /s /q build
