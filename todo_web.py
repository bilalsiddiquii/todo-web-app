from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import json
import os
import openai
import base64
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "your_secret_key"
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/")
def home():
    return render_template("chat.html", username="Guest")

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

    img_bytes = image.read()
    b64_image = base64.b64encode(img_bytes).decode("utf-8")
    data_uri = f"data:{image.mimetype};base64,{b64_image}"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-vision",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": message},
                        {"type": "image_url", "image_url": {"url": data_uri}}
                    ]
                }
            ],
            max_tokens=800
        )
        reply = response["choices"][0]["message"]["content"]
        return jsonify({"reply": reply})
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("Using fallback vision reply.")
        return jsonify({"reply": "👁️ I received the image, but I can't analyze it at the moment. Please ensure your API key supports GPT-4 Vision or check the latest model name."})

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
