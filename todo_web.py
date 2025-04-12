from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)
FILENAME = "tasks.json"

def load_tasks():
    if os.path.exists(FILENAME):
        with open(FILENAME, "r") as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(FILENAME, "w") as f:
        json.dump(tasks, f)

@app.route("/")
def index():
    tasks = load_tasks()
    return render_template("index.html", tasks=tasks)

@app.route("/add", methods=["POST"])
def add():
    desc = request.form["task"]
    tasks = load_tasks()
    tasks.append({"description": desc, "done": False})
    save_tasks(tasks)
    return redirect(url_for("index"))

@app.route("/done/<int:index>")
def done(index):
    tasks = load_tasks()
    tasks[index]["done"] = True
    save_tasks(tasks)
    return redirect(url_for("index"))

@app.route("/delete/<int:index>")
def delete(index):
    tasks = load_tasks()
    if 0 <= index < len(tasks):
        del tasks[index]
    save_tasks(tasks)
    return redirect(url_for("index"))

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
