from flask import Flask, render_template
import datetime, random

app = Flask(__name__)

@app.route("/")
def dashboard():
    emotions = ["❤️ Calm", "🔥 Focused", "⚡ Inspired", "💫 Analytical", "💭 Reflective"]
    current_emotion = random.choice(emotions)

    context_memory = [
        {"timestamp": "2025-10-23 21:35", "event": "Analyzed token trends for WENBNB."},
        {"timestamp": "2025-10-23 21:42", "event": "User Asshok requested AI analysis ✅"},
        {"timestamp": "2025-10-23 21:45", "event": "Generated meme tone: 'Hopeful'."}
    ]

    data = {
        "tokens": 24,
        "users": 342,
        "load": "Normal"
    }

    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    return render_template("dashboard.html",
                           timestamp=timestamp,
                           emotion=current_emotion,
                           data=data,
                           context_memory=context_memory)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
