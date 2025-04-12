import tkinter as tk
from tkinter import messagebox
import json
import os

FILENAME = "tasks.json"

# --- Load/Save ---
def load_tasks():
    if os.path.exists(FILENAME):
        with open(FILENAME, "r") as f:
            return json.load(f)
    return []

def save_tasks():
    with open(FILENAME, "w") as f:
        json.dump(tasks, f)

# --- Functions ---
def add_task():
    desc = entry.get().strip()
    if desc:
        task = {"description": desc, "done": False}
        tasks.append(task)
        save_tasks()
        entry.delete(0, tk.END)
        refresh_list()
    else:
        messagebox.showwarning("Empty", "Task can't be empty.")

def mark_done():
    selected = listbox.curselection()
    if selected:
        index = selected[0]
        tasks[index]["done"] = True
        save_tasks()
        refresh_list()

def delete_task():
    selected = listbox.curselection()
    if selected:
        index = selected[0]
        del tasks[index]
        save_tasks()
        refresh_list()

def clear_completed():
    global tasks
    tasks = [task for task in tasks if not task["done"]]
    save_tasks()
    refresh_list()

def refresh_list():
    listbox.delete(0, tk.END)
    for task in tasks:
        status = "✔" if task["done"] else "✘"
        listbox.insert(tk.END, f'{task["description"]} [{status}]')

# --- GUI Setup ---
tasks = load_tasks()

root = tk.Tk()
root.title("To-Do List App")
root.geometry("500x350")
root.configure(bg="#f7f7f7")

entry = tk.Entry(root, width=40, bg="white")
entry.pack(pady=10)
entry.bind("<Return>", lambda event: add_task())

btn_frame = tk.Frame(root, bg="#f7f7f7")
btn_frame.pack()

tk.Button(btn_frame, text="Add Task", width=12, command=add_task).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="Mark Done", width=12, command=mark_done).grid(row=0, column=1, padx=5)
tk.Button(btn_frame, text="Delete Task", width=12, command=delete_task).grid(row=0, column=2, padx=5)
tk.Button(btn_frame, text="Clear Completed", width=15, command=clear_completed).grid(row=0, column=3, padx=5)

listbox = tk.Listbox(root, width=60, height=10, bg="white")
listbox.pack(pady=10)

refresh_list()
root.mainloop()
