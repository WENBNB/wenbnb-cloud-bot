"""
dashboard/dashboard.py  —  WENBNB Neural Dashboard v1.5 (Live Reactive Edition)

Features:
 - Auto-refresh (every 15s) via /live_data
 - /update_activity POST endpoint for bot -> dashboard sync
 - R2/S3 status + last backup check
 - Heartbeat (turns red when no bot activity)
 - Admin gating via DASHBOARD_PUBLIC / DASHBOARD_SECRET_KEY
 - Safe log redaction (no secrets shown)
"""

import os
import time
import threading
import psutil
import boto3
from datetime import datetime, timezone, timedelta
from flask import Flask, render_template_string, jsonify, request, abort

app = Flask(__name__)

# -------------------------
# Config via env (set in Render)
# -------------------------
APP_PORT = int(os.getenv("PORT", "10000"))
R2_ACCESS_KEY = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")
R2_ENDPOINT = os.getenv("R2_ENDPOINT_URL")

DASHBOARD_PUBLIC = os.getenv("DASHBOARD_PUBLIC", "true").lower() == "true"
DASHBOARD_SECRET_KEY = os.getenv("DASHBOARD_SECRET_KEY", "")  # required if public=false

ENGINE_VERSION = os.getenv("ENGINE_VERSION", "v5.0")
CORE_VERSION = os.getenv("CORE_VERSION", "v3.0")
NEURAL_TAGLINE = f"🤖 WENBNB Neural Engine {ENGINE_VERSION} — Core {CORE_VERSION}"

# Live memory for events (thread-safe lock)
EVENTS = []
EVENTS_LOCK = threading.Lock()
EVENTS_MAX = 60

# Last activity timestamp (UTC)
LAST_ACTIVITY = None
LAST_ACTIVITY_LOCK = threading.Lock()

# -------------------------
# Utilities
# -------------------------
def now_iso():
    return datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()

def safe_redact(text: str) -> str:
    # Basic redaction: hide long hex strings / keys (very naive but helpful)
    import re
    text = re.sub(r"(0x[a-fA-F0-9]{8,})", r"<redacted>", text)
    text = re.sub(r"([A-Za-z0-9_\-]{30,})", r"<redacted>", text)
    return text

def add_event(event: str, source: str = "bot"):
    global LAST_ACTIVITY
    ev = {
        "timestamp": now_iso(),
        "source": source,
        "event": safe_redact(event)[:600]  # limit length
    }
    with EVENTS_LOCK:
        EVENTS.append(ev)
        if len(EVENTS) > EVENTS_MAX:
            EVENTS.pop(0)
    with LAST_ACTIVITY_LOCK:
        LAST_ACTIVITY = datetime.utcnow().replace(tzinfo=timezone.utc)

# -------------------------
# System info & R2 status
# -------------------------
def get_system_info():
    cpu = psutil.cpu_percent(interval=0.3)
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    uptime = time.time() - psutil.boot_time()
    return {
        "cpu": round(cpu, 1),
        "mem": round(mem, 1),
        "disk": round(disk, 1),
        "uptime_seconds": int(uptime)
    }

def get_r2_status():
    if not (R2_ACCESS_KEY and R2_SECRET_KEY and R2_BUCKET_NAME and R2_ENDPOINT):
        return {"connected": False}
    try:
        session = boto3.session.Session()
        s3 = session.client(
            service_name="s3",
            endpoint_url=R2_ENDPOINT,
            aws_access_key_id=R2_ACCESS_KEY,
            aws_secret_access_key=R2_SECRET_KEY,
        )
        objs = s3.list_objects_v2(Bucket=R2_BUCKET_NAME, MaxKeys=5)
        if "Contents" in objs and len(objs["Contents"]) > 0:
            last = objs["Contents"][-1]["LastModified"]
            # ensure iso
            last_iso = last.astimezone(timezone.utc).isoformat()
            return {"connected": True, "bucket": R2_BUCKET_NAME, "last_backup": last_iso}
        else:
            return {"connected": True, "bucket": R2_BUCKET_NAME, "last_backup": "none"}
    except Exception as e:
        add_event(f"R2 check failed: {e}", source="dashboard")
        return {"connected": False, "error": str(e)}

# -------------------------
# Security gate helper
# -------------------------
def require_key_if_needed(req: request):
    if DASHBOARD_PUBLIC:
        return True
    # check header or query param
    key = req.headers.get("X-DASH-KEY") or req.args.get("key")
    if key and DASHBOARD_SECRET_KEY and key == DASHBOARD_SECRET_KEY:
        return True
    abort(401)

# -------------------------
# API Endpoints
# -------------------------
@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok", "engine": ENGINE_VERSION, "core": CORE_VERSION, "time": now_iso()})

@app.route("/update_activity", methods=["POST"])
def update_activity():
    # Called by bot: POST JSON { "event": "Price command triggered by @user", "level": "info" }
    try:
        require_key_if_needed(request)
        j = request.get_json(force=True)
        ev = j.get("event") or j.get("msg") or "activity"
        src = j.get("source") or "bot"
        add_event(ev, source=src)
        return jsonify({"status": "ok", "time": now_iso()})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 400

@app.route("/live_data", methods=["GET"])
def live_data():
    require_key_if_needed(request)
    sys = get_system_info()
    r2 = get_r2_status()
    with EVENTS_LOCK:
        events_copy = list(EVENTS)[-20:][::-1]  # recent first
    with LAST_ACTIVITY_LOCK:
        last = LAST_ACTIVITY.isoformat() if LAST_ACTIVITY else None
    # heartbeat: offline if no activity in last 45s
    heartbeat = "ok"
    if last:
        last_dt = LAST_ACTIVITY
        delta = datetime.utcnow().replace(tzinfo=timezone.utc) - last_dt
        if delta > timedelta(seconds=45):
            heartbeat = "stale"
    else:
        heartbeat = "no_activity"
    return jsonify({
        "system": sys,
        "r2": r2,
        "events": events_copy,
        "last_activity": last,
        "heartbeat": heartbeat,
        "tagline": NEURAL_TAGLINE,
        "time": now_iso()
    })

# -------------------------
# Simple index with JS polling (auto refresh)
# -------------------------
INDEX_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>WENBNB Neural Dashboard v1.5</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <style>
    :root{
      --bg:#05060a; --panel:#0e1116; --accent:#00ffd1; --muted:#9aa5b1;
      --card-shadow: 0 6px 24px rgba(0,255,209,0.06);
    }
    body{font-family:Inter, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
      background:linear-gradient(180deg,#04050a,#081018); margin:0; color:#e6f8f0;}
    .wrap{max-width:1100px;margin:28px auto;padding:20px;}
    header{display:flex;align-items:center;justify-content:space-between;margin-bottom:18px;}
    h1{font-size:20px;margin:0;color:var(--accent);}
    .tag{color:var(--muted);font-size:12px}
    .grid{display:grid;grid-template-columns:1fr 340px;gap:18px;}
    .card{background:var(--panel);border-radius:12px;padding:14px;box-shadow:var(--card-shadow);}
    .stat{display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px dashed rgba(255,255,255,0.03);}
    .stat:last-child{border-bottom:0}
    .label{color:var(--muted);font-size:13px}
    .value{font-weight:700;color:#fff}
    .events{max-height:360px;overflow:auto;padding-top:8px;}
    .ev{padding:8px;border-radius:8px;margin-bottom:8px;background:linear-gradient(90deg, rgba(0,255,209,0.02), transparent);}
    .ev small{color:var(--muted);display:block;margin-bottom:4px;font-size:12px}
    .heartbeat{display:inline-block;padding:6px 10px;border-radius:999px;font-weight:700}
    .hb-ok{background:rgba(0,255,209,0.12);color:var(--accent)}
    .hb-stale{background:rgba(255,100,100,0.08);color:#ff8a8a}
    footer{margin-top:18px;color:var(--muted);font-size:13px;text-align:center}
    .r2{font-size:13px;color:var(--muted);margin-top:8px}
    .muted{color:var(--muted)}
    .btn{background:#071021;border:1px solid rgba(255,255,255,0.02);padding:8px 12px;border-radius:8px;color:var(--accent);cursor:pointer}
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <div>
        <h1>🚀 WENBNB Neural Dashboard <small style="color:var(--muted)">v1.5</small></h1>
        <div class="tag">{{ tagline }}</div>
      </div>
      <div>
        <button class="btn" onclick="manualRefresh()">Refresh</button>
      </div>
    </header>

    <div class="grid">
      <div>
        <div class="card">
          <h3 style="margin-top:0">🧠 System Health</h3>
          <div class="stat"><div class="label">CPU</div><div class="value" id="cpu">—</div></div>
          <div class="stat"><div class="label">Memory</div><div class="value" id="mem">—</div></div>
          <div class="stat"><div class="label">Disk</div><div class="value" id="disk">—</div></div>
          <div style="margin-top:8px"><span class="label">Heartbeat</span> <span id="heartbeat" class="heartbeat hb-ok">—</span></div>
        </div>

        <div class="card" style="margin-top:16px">
          <h3 style="margin-top:0">📜 Activity Feed</h3>
          <div class="events" id="events">Loading…</div>
        </div>
      </div>

      <div>
        <div class="card">
          <h3 style="margin-top:0">☁️ Cloud Sync (R2 / S3)</h3>
          <div id="r2status" class="r2">Checking…</div>
        </div>

        <div class="card" style="margin-top:16px">
          <h3 style="margin-top:0">ℹ️ Info</h3>
          <div class="muted">Last update: <span id="lastupdate">—</span></div>
          <div class="muted" style="margin-top:8px">Public mode: <strong>{{ public_mode }}</strong></div>
          <div style="margin-top:12px"><small class="muted">Tip: Your bot should POST /update_activity when commands run to populate this feed.</small></div>
        </div>
      </div>
    </div>

    <footer>
      <div>{{ tagline }}</div>
    </footer>
  </div>

  <script>
    const POLL_INTERVAL = 15000; // ms
    const API = "/live_data";
    let timer = null;

    async function fetchData(){
      try {
        const res = await fetch(API);
        if(!res.ok){ throw new Error("HTTP " + res.status); }
        const j = await res.json();
        document.getElementById("cpu").textContent = j.system.cpu + "%";
        document.getElementById("mem").textContent = j.system.mem + "%";
        document.getElementById("disk").textContent = j.system.disk + "%";
        document.getElementById("lastupdate").textContent = new Date(j.time).toLocaleString();
        // heartbeat
        const hb = document.getElementById("heartbeat");
        if(j.heartbeat === "ok"){ hb.className = "heartbeat hb-ok"; hb.textContent = "ACTIVE"; }
        else if(j.heartbeat === "stale"){ hb.className = "heartbeat hb-stale"; hb.textContent = "STALE"; }
        else { hb.className = "heartbeat hb-stale"; hb.textContent = "NO ACTIVITY"; }

        // events
        const events = j.events || [];
        const evdom = document.getElementById("events");
        if(events.length === 0){ evdom.innerHTML = "<div class='muted'>No recent events</div>"; }
        else {
          evdom.innerHTML = "";
          for(const e of events){
            const node = document.createElement("div");
            node.className = "ev";
            node.innerHTML = `<small>${new Date(e.timestamp).toLocaleTimeString()}</small><div>${escapeHtml(e.event)}</div>`;
            evdom.appendChild(node);
          }
        }

        // r2
        const r2 = j.r2 || {};
        const r2node = document.getElementById("r2status");
        if(r2.connected){ r2node.innerHTML = "✅ Connected to <strong>" + (r2.bucket||"bucket") + "</strong><br/>Last backup: " + (r2.last_backup||"n/a"); }
        else { r2node.innerHTML = "⚠️ No cloud connection configured or connection failed."; }

      } catch(err){
        console.warn("Fetch error:", err);
        const ev = document.getElementById("events");
        ev.innerHTML = "<div class='muted'>Unable to fetch live data.</div>";
      }
    }

    function escapeHtml(unsafe) {
      return unsafe
           .replace(/&/g, "&amp;")
           .replace(/</g, "&lt;")
           .replace(/>/g, "&gt;")
           .replace(/"/g, "&quot;")
           .replace(/'/g, "&#039;");
    }

    function manualRefresh(){
      fetchData();
    }

    // start polling
    fetchData();
    timer = setInterval(fetchData, POLL_INTERVAL);
  </script>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    # if not public, require key param/header
    try:
        require = not DASHBOARD_PUBLIC
        if require:
            key = request.args.get("key") or request.headers.get("X-DASH-KEY")
            if not key or key != DASHBOARD_SECRET_KEY:
                return ("Unauthorized - dashboard access protected", 401)
    except Exception:
        return ("Unauthorized", 401)
    return render_template_string(INDEX_HTML, tagline=NEURAL_TAGLINE, public_mode=str(DASHBOARD_PUBLIC))

# -------------------------
# Background: optional housekeeping (keeps events trimmed)
# -------------------------
def housekeeping():
    while True:
        with EVENTS_LOCK:
            if len(EVENTS) > EVENTS_MAX:
                del EVENTS[0:len(EVENTS)-EVENTS_MAX]
        time.sleep(10)

# start housekeeping thread
threading.Thread(target=housekeeping, daemon=True).start()

# -------------------------
# Run server
# -------------------------
if __name__ == "__main__":
    # add a small startup event
    add_event("Dashboard v1.5 started", source="dashboard")
    app.run(host="0.0.0.0", port=APP_PORT)
