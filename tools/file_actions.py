import os


# ==========================================
# SAFE PROJECT DIRECTORY
# ==========================================

BASE_DIR = os.path.abspath(".")


def safe_path(filename):

    requested_path = os.path.abspath(
        os.path.join(BASE_DIR, filename)
    )

    # Prevent access outside MANU project
    if not requested_path.startswith(BASE_DIR):

        raise PermissionError(
            "Access outside the MANU project is not allowed."
        )

    return requested_path


# ==========================================
# READ FILE
# ==========================================

def read_file(filename):

    try:

        path = safe_path(filename)

        if not os.path.isfile(path):

            return {
                "error": "File not found."
            }

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            content = file.read()

        return {
            "file": filename,
            "content": content
        }

    except UnicodeDecodeError:

        return {
            "error": "This file is not a readable text file."
        }

    except PermissionError as e:

        return {
            "error": str(e)
        }

    except OSError as e:

        return {
            "error": f"Could not read file: {e}"
        }


# ==========================================
# WRITE FILE
# ==========================================

def write_file(filename, content):

    try:

        path = safe_path(filename)

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(content)

        return {
            "file": filename,
            "status": "created",
            "message": "File written successfully."
        }

    except PermissionError as e:

        return {
            "error": str(e)
        }

    except OSError as e:

        return {
            "error": f"Could not write file: {e}"
        }


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    print("MANU File Actions")
    print("=================")

    result = write_file(
        "manu_test.txt",
        "MANU V0.6 test successful."
    )

    print(result)

    result = read_file(
        "manu_test.txt"
    )

    print(result)