# PyInstaller build script (name: mineplace)
pyinstaller --onefile --add-data "assets:assets" main.py --name mineplace --noconsole # For Linux

# Remove useless files
rm -rf build mineplace.spec
