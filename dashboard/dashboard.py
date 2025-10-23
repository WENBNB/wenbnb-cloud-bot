# dashboard/dashboard.py
import os
import time
import queue
import threading
from flask import Flask, render_template, jsonify, request, Response, abort
from datetime import datetime

# Simple in-memory event queue for streaming logs
log_queue = queue.Queue()

def push_log(level, msg):
    payload = {
        "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "level": level,
        "message": msg
    }
    log_queue.put(payload)

# Example: Some startup logs
push_log("info", "WENBNB Dashboard initializing...")
push_log("info", "Neural Engine connector pending...")

app = Flask(__name__, template_folder="templates", static_folder="static")

# Basic status endpoint (bot code can call POST /update_status)
status_state = {
    "status": "starting",
    "uptime": "0s",
    "users": 0,
    "version": os.getenv("BOT_SIGNATURE", "WENBNB Neural Engine")
}

@app.route("/")
def index():
    return render_template("index.html", status=status_state)

@app.route("/status", methods=["GET"])
def get_status():
    return jsonify(status_state)

# Endpoint for bot to POST live status updates (optional)
@app.route("/update_status", methods=["POST"])
def update_status():
    key = os.getenv("DASHBOARD_KEY", "")
    header_key = request.headers.get("Authorization", "")
    if key and header_key != f"Bearer {key}":
        abort(401)

    data = request.get_json() or {}
    # Update only allowed keys
    for k in ("status", "uptime", "users"):
        if k in data:
            status_state[k] = data[k]
    push_log("info", f"Status updated via bot: {data}")
    return jsonify({"ok": True})

# SSE stream for logs
def event_stream():
    # long-polling: yield queued logs as Server-Sent Events
    while True:
        try:
            item = log_queue.get(timeout=0.5)
            yield f"data: {item}\\n\\n"
        except queue.Empty:
            # heartbeat to keep connection alive
            yield "data: {\"heartbeat\": true}\\n\\n"
            time.sleep(0.5)

@app.route("/stream")
def stream():
    return Response(event_stream(), mimetype="text/event-stream")

# Admin action endpoint
@app.route("/action", methods=["POST"])
def action():
    key = os.getenv("DASHBOARD_KEY", "")
    header_key = request.headers.get("Authorization", "")
    if key and header_key != f"Bearer {key}":
        return jsonify({"error": "unauthorized"}), 401

    body = request.get_json() or {}
    cmd = body.get("cmd")
    push_log("admin", f"Received action: {cmd}")

    # Example admin actions: restart_bot, clear_cache, trigger_backup
    if cmd == "restart_bot":
        # plugin: place a flag file or call a local function to signal restart
        push_log("warn", "Restart requested. (Manual restart required by Render or process manager)")
        return jsonify({"ok": True, "message": "Restart requested (see logs)."})
    elif cmd == "clear_cache":
        push_log("info", "Clearing caches (simulated).")
        return jsonify({"ok": True, "message": "Cache cleared."})
    elif cmd == "trigger_backup":
        # Offload backup to another thread to avoid blocking
        def backup_job():
            push_log("info", "Backup started...")
            time.sleep(2)
            push_log("info", "Backup completed: backup_{}.zip".format(datetime.utcnow().strftime("%Y%m%d%H%M")))
        threading.Thread(target=backup_job, daemon=True).start()
        return jsonify({"ok": True, "message": "Backup started."})
    else:
        push_log("error", f"Unknown admin command: {cmd}")
        return jsonify({"error": "unknown_command"}), 400

# Simple endpoint to fetch recent logs (non-stream)
@app.route("/logs", methods=["GET"])
def logs():
    # For demo: return last N logs — in production you would read from a persistent log
    logs_list = []
    while not log_queue.empty():
        try:
            logs_list.append(log_queue.get_nowait())
        except Exception:
            break
    # push them back so stream still continues (best-effort)
    for item in logs_list:
        log_queue.put(item)
    return jsonify({"logs": logs_list})

# Health route (used by healthchecks)
@app.route("/healthz")
def healthz():
    return jsonify({"status": "ok", "time": datetime.utcnow().isoformat()})

if __name__ == "__main__":
    push_log("info", "Dashboard starting server...")
    port_str = os.getenv("PORT", "10000")
    try:
        port = int(port_str) if port_str else 10000
    except ValueError:
        port = 10000
    print(f"🚀 Dashboard running on port {port} ...")
    app.run(host="0.0.0.0", port=port)
