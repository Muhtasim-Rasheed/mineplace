import os

def ensureappdir():
    # Makes a ~/mineplace/saves directory or %APPDATA%/mineplace/saves on Windows if it doesn't exist
    folder_to_save = ""
    if os.name == "nt":
        folder_to_save = os.getenv("APPDATA")
    else:
        folder_to_save = os.path.expanduser("~")
    folder_to_save = os.path.join(folder_to_save, "mineplace", "saves")

    if not os.path.exists(folder_to_save):
        os.makedirs(folder_to_save)
