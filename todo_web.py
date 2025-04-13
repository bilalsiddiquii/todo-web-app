from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import json
import os
import openai
import base64
from werkzeug.utils import secure_filename
import random

app = Flask(__name__)
app.secret_key = "your_secret_key"
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/")
def home():
    username = session.get("username", "Guest")
    return render_template("chat.html", username=username)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        if username:
            session["username"] = username
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Please enter a username")
    return render_template("login.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_msg = data.get("message")
    mode = data.get("mode", "assistant")
    if not user_msg:
        return jsonify({"error": "No message provided"}), 400

    if "chat" not in session:
        session["chat"] = []

    mode_prompts = {
        "assistant": "You are a helpful assistant.",
        "coder": "You are a programming expert. Answer all coding questions with concise and accurate code examples.",
        "creative": "You are a poetic and creative writer. Respond in imaginative and artistic ways.",
        "therapist": "You are a kind and thoughtful therapist helping users with emotional clarity.",
        "teacher": "You are a patient teacher explaining concepts clearly and with examples."
    }

    session["chat"] = [{"role": "system", "content": mode_prompts.get(mode, mode_prompts["assistant"])}] + session["chat"]
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

@app.route("/vision", methods=["POST"])
def vision():
    message = request.form.get("message", "")
    mode = request.form.get("mode", "assistant")
    image = request.files.get("image")

    if not image:
        return jsonify({"reply": "⚠️ No image uploaded."}), 400

    # Fallback mock captions
    captions = [
        "Looks like a peaceful sunset at the beach 🌅",
        "That’s a cute cat! 🐱",
        "It seems to be a street filled with cars 🚗",
        "I'm guessing this is a delicious plate of food 🍝",
        "Looks like a group of people having fun 🎉",
        "Hmm... looks like an abstract painting 🎨",
        "Maybe a forest trail or some greenery 🌲"
    ]

    # Randomly return a fake caption
    fake_reply = random.choice(captions)
    print("Fallback vision used. Sending fake caption:", fake_reply)
    return jsonify({"reply": fake_reply})

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/export")
def export():
    return jsonify(session.get("chat", []))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
