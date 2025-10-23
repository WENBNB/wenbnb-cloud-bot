from flask import Flask, render_template, jsonify
import datetime, random, threading, time

app = Flask(__name__)

AI_STATE = {
    "emotion": "💫 Analytical",
    "activity": 42,
    "logs": []
}

def simulate_ai_pulse():
    while True:
        AI_STATE["emotion"] = random.choice(["❤️ Calm", "🔥 Focused", "⚡ Inspired", "💫 Analytical", "💭 Reflective"])
        AI_STATE["activity"] = random.randint(20, 100)
        AI_STATE["logs"].append({
            "timestamp": datetime.datetime.utcnow().strftime("%H:%M:%S"),
            "event": f"AI Neural Pulse — emotion shifted to {AI_STATE['emotion']}"
        })
        if len(AI_STATE["logs"]) > 8:
            AI_STATE["logs"].pop(0)
        time.sleep(3)

@app.route("/")
def dashboard():
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    return render_template("dashboard.html", timestamp=timestamp)

@app.route("/live_data")
def live_data():
    return jsonify(AI_STATE)

if __name__ == "__main__":
    threading.Thread(target=simulate_ai_pulse, daemon=True).start()
    app.run(host="0.0.0.0", port=5050)
