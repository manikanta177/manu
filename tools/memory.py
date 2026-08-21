# ==========================================
# MANU V1.1 MEMORY SYSTEM
# ==========================================

import json
import os


FACTS_FILE = "facts.json"


# ==========================================
# LOAD FACTS
# ==========================================

def load_facts():

    if not os.path.exists(FACTS_FILE):

        return {}

    try:

        with open(
            FACTS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if isinstance(data, dict):

                return data

            return {}

    except (
        json.JSONDecodeError,
        OSError
    ):

        return {}


# ==========================================
# SAVE FACTS
# ==========================================

def save_facts(facts):

    try:

        with open(
            FACTS_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                facts,
                file,
                indent=2,
                ensure_ascii=False
            )

        return True

    except OSError:

        return False


# ==========================================
# REMEMBER
# ==========================================

def remember(key, value):

    key = str(key).strip()
    value = str(value).strip()

    if not key:

        return {
            "success": False,
            "error": "Memory key cannot be empty."
        }

    if not value:

        return {
            "success": False,
            "error": "Memory value cannot be empty."
        }

    facts = load_facts()

    facts[key] = value

    if not save_facts(facts):

        return {
            "success": False,
            "error": "Could not save memory."
        }

    return {
        "success": True,
        "message": "Fact remembered successfully.",
        "key": key,
        "value": value
    }


# ==========================================
# RECALL
# ==========================================

def recall(key):

    key = str(key).strip()

    if not key:

        return {
            "success": False,
            "error": "Memory key cannot be empty."
        }

    facts = load_facts()

    if key not in facts:

        return {
            "success": False,
            "error": f"No memory found for '{key}'."
        }

    return {
        "success": True,
        "key": key,
        "value": facts[key]
    }


# ==========================================
# LIST FACTS
# ==========================================

def list_facts():

    facts = load_facts()

    return {
        "success": True,
        "facts": facts
    }


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    print("MANU Memory V1.1")
    print("================")

    print()

    print(
        "Current facts:"
    )

    print(
        list_facts()
    )
