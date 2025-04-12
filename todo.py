import json
import os

FILENAME = "tasks.json"

def save_tasks():
    with open(FILENAME, "w") as file:
        json.dump(tasks, file)
    
def load_tasks():
    global tasks
    if os.path.exists(FILENAME):
        with open(FILENAME, "r") as file:
            tasks = json.load(file)
    else:
        tasks = []
    save_tasks()

tasks = []

def show_tasks():
    if not tasks:
        print("No tasks yet.")
    else:
        for task in tasks:
            status = "✔" if task["done"] else "✘"
            print(f'{task["id"]}. {task["description"]} [{status}]')
            save_tasks()

def add_task(desc):
    task_id = len(tasks) + 1
    task = {"id": task_id, "description": desc, "done": False}
    tasks.append(task)
    save_tasks()

def mark_done(task_id):
    for task in tasks:
        if task["id"] == task_id:
            task["done"] = True
            break
    save_tasks()
def delete_task(task_id):
    global tasks
    tasks = [task for task in tasks if task["id"] != task_id]
    save_tasks()

load_tasks()

# --- Main app loop ---
while True:
    print("\n--- To-Do App Menu ---")
    print("1. View Tasks")
    print("2. Add Task")
    print("3. Mark Task as Done")
    print("4. Delete Task")
    print("5. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        show_tasks()
    elif choice == "2":
        desc = input("Enter task description: ")
        add_task(desc)
    elif choice == "3":
        task_id = int(input("Enter task ID to mark done: "))
        mark_done(task_id)
    elif choice == "4":
        task_id = int(input("Enter task ID to delete: "))
        delete_task(task_id)
    elif choice == "5":
        print("Goodbye!")
        break
    else:
        print("Invalid choice. Try again.")
