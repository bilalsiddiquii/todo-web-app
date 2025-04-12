from flask import Flask, render_template, request, redirect, url_for, jsonify, session, send_file
import json
import os
import openai
import uuid
from io import StringIO

# ✅ Set API key for OpenAI v0.28
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")  # For session support
FILENAME = "tasks.json"

# ✅ Load & save tasks for the to-do list
def load_tasks():
    if os.path.exists(FILENAME):
        with open(FILENAME, "r") as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(FILENAME, "w") as f:
        json.dump(tasks, f)

# ✅ Routes for your to-do app
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

@app.route("/zones")
def zones():
    return render_template("zones.html")

# ✅ Auth system: simple username session
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        if username:
            session["username"] = username
            session["chat"] = []
            return redirect(url_for("chatui"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ✅ AI Chat endpoint with memory
@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message")
    if not user_msg:
        return jsonify({"error": "No message provided"}), 400

    # Store memory in session
    if "chat" not in session:
        session["chat"] = []

    session["chat"].append({"role": "user", "content": user_msg})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=session["chat"]
        )
        reply = response["choices"][0]["message"]["content"]
        session["chat"].append({"role": "assistant", "content": reply})
        return jsonify({"reply": reply})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"reply": "⚠️ Failed to get a response from OpenAI."})

# ✅ Webpage for AI chat UI
@app.route("/chatui")
def chatui():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("chat.html", username=session["username"])  # username passed in

# ✅ Export chat to .txt
@app.route("/export")
def export_chat():
    if "chat" not in session:
        return "No chat to export", 400
    buffer = StringIO()
    for msg in session["chat"]:
        buffer.write(f"{msg['role'].capitalize()}: {msg['content']}\n\n")
    buffer.seek(0)
    return send_file(buffer, mimetype="text/plain", as_attachment=True, download_name="chat_history.txt")

# ✅ Entry point
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
