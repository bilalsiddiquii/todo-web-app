from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
import openai

# ✅ Set API key for OpenAI v0.28
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
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

# ✅ AI Chat endpoint (OpenAI v0.28 compatible)
@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message")
    if not user_msg:
        return jsonify({"error": "No message provided"}), 400

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_msg}]
        )
        reply = response["choices"][0]["message"]["content"]
        return jsonify({"reply": reply})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"reply": "⚠️ Failed to get a response from OpenAI."})

# ✅ Webpage for AI chat UI
@app.route("/chatui")
def chatui():
    return render_template("chat.html")

# ✅ Entry point
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
