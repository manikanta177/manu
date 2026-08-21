import os


def list_files(folder="."):
    try:
        items = os.listdir(folder)

        if not items:
            return ["Folder is empty."]

        return items

    except FileNotFoundError:
        return ["Folder not found."]

    except PermissionError:
        return ["Permission denied."]


if __name__ == "__main__":

    print("MANU File Explorer")
    print("==================")

    files = list_files(".")

    for item in files:
        print(item)