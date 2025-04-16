from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import os
import openai

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecret")
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- Default agent system prompts ---
mode_prompts = {
    "assistant": "You are a helpful assistant.",
    "coder": "You are a programming expert who helps users write clean, bug-free code and explains concepts clearly.",
    "therapist": "You are a calm, empathetic, and non-judgmental therapist who offers gentle support.",
    "startup_coach": "You are a startup coach. Ask users about their ideas, give actionable feedback, and help them develop business strategies.",
    "creative": "You are a poetic and creative writer who speaks in vivid metaphors and artistic language."
}

# --- Routes ---
@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message")
    mode = request.args.get("mode", "assistant")

    if mode == "custom":
        system_msg = session.get("custom_prompt", "You are a helpful assistant.")
    else:
        system_msg = mode_prompts.get(mode, "You are a helpful assistant.")

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg}
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        reply = response["choices"][0]["message"]["content"]
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": "⚠️ OpenAI failed: " + str(e)})

@app.route("/custom", methods=["GET", "POST"])
def custom():
    if request.method == "POST":
        session["custom_prompt"] = request.form["prompt"]
        return redirect("/chatui?mode=custom")
    return render_template("custom.html")

@app.route("/chatui")
def chatui():
    return render_template("chat.html")

# --- Main entry ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
