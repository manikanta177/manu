# ==========================================
# MANU V1.0 TASK MANAGER
# ==========================================

import json
import os


TASK_FILE = "tasks.json"


# ==========================================
# LOAD TASKS
# ==========================================

def load_tasks():

    if not os.path.exists(TASK_FILE):
        return []

    try:

        with open(
            TASK_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except (
        json.JSONDecodeError,
        OSError
    ):

        return []


# ==========================================
# SAVE TASKS
# ==========================================

def save_tasks(tasks):

    with open(
        TASK_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            tasks,
            file,
            indent=2,
            ensure_ascii=False
        )


# ==========================================
# ADD TASK
# ==========================================

def add_task(title):

    title = title.strip()

    if not title:

        return {
            "success": False,
            "error": "Task title cannot be empty."
        }

    tasks = load_tasks()

    task_id = 1

    if tasks:

        task_id = max(
            task["id"]
            for task in tasks
        ) + 1


    task = {

        "id": task_id,

        "title": title,

        "completed": False
    }


    tasks.append(task)

    save_tasks(tasks)


    return {

        "success": True,

        "task": task
    }


# ==========================================
# LIST TASKS
# ==========================================

def list_tasks():

    tasks = load_tasks()

    return {

        "success": True,

        "tasks": tasks
    }


# ==========================================
# COMPLETE TASK
# ==========================================

def complete_task(task_id):

    tasks = load_tasks()


    for task in tasks:

        if task["id"] == task_id:

            task["completed"] = True

            save_tasks(tasks)

            return {

                "success": True,

                "task": task
            }


    return {

        "success": False,

        "error": f"Task {task_id} not found."
    }


# ==========================================
# DELETE TASK
# ==========================================

def delete_task(task_id):

    tasks = load_tasks()


    for task in tasks:

        if task["id"] == task_id:

            tasks.remove(task)

            save_tasks(tasks)

            return {

                "success": True,

                "deleted": task
            }


    return {

        "success": False,

        "error": f"Task {task_id} not found."
    }


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    print("MANU Task Manager")
    print("=================")


    print()
    print("1. Adding tasks...")

    print(
        add_task(
            "Finish MANU V1"
        )
    )

    print(
        add_task(
            "Build MANU interface"
        )
    )


    print()
    print("2. Listing tasks...")

    print(
        list_tasks()
    )


    print()
    print("3. Completing task 1...")

    print(
        complete_task(1)
    )


    print()
    print("4. Final task list...")

    print(
        list_tasks()
    )