// dashboard/static/main.js

(function(){
  const feed = document.getElementById("logfeed");
  const statusEl = document.getElementById("bot-status");
  const uptimeEl = document.getElementById("bot-uptime");
  const usersEl = document.getElementById("bot-users");

  function appendLog(item){
    try{
      const data = typeof item === "string" ? JSON.parse(item) : item;
      if (data.heartbeat) return;
      const div = document.createElement("div");
      div.className = "log-item";
      const lvl = document.createElement("div");
      lvl.className = "lvl " + (data.level || "info");
      lvl.innerText = (data.level || "info").toUpperCase();
      const txt = document.createElement("div");
      txt.innerHTML = `<small style="color:#9aa0a6">${data.time}</small><br>${escapeHtml(data.message)}`;
      div.appendChild(txt);
      div.appendChild(lvl);
      feed.prepend(div);
      // limit feed
      if (feed.children.length > 200) feed.removeChild(feed.lastChild);
    } catch(e){
      // ignore
    }
  }

  function escapeHtml(unsafe) {
    return unsafe
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  // SSE stream
  const src = new EventSource("/stream");
  src.onmessage = function(e){
    try{
      appendLog(e.data);
    } catch(err){}
  };
  src.onerror = function(){
    console.warn("SSE error");
  };

  // Periodic status fetch
  async function refreshStatus(){
    try{
      let res = await fetch("/status");
      let j = await res.json();
      statusEl.innerText = j.status || "—";
      uptimeEl.innerText = j.uptime || "—";
      usersEl.innerText = j.users || 0;
    } catch(e){
      statusEl.innerText = "offline";
    }
  }
  setInterval(refreshStatus, 5000);
  refreshStatus();

  // Admin actions
  async function sendAction(cmd){
    const key = "";
    try{
      const res = await fetch("/action", {
        method: "POST",
        headers: {
          "Content-Type":"application/json",
          "Authorization": key ? `Bearer ${key}` : ""
        },
        body: JSON.stringify({cmd})
      });
      const j = await res.json();
      appendLog(JSON.stringify({time:new Date().toISOString(), level:"admin", message: `Action ${cmd} → ${JSON.stringify(j)}`}));
    } catch(e){
      appendLog(JSON.stringify({time:new Date().toISOString(), level:"error", message: `Action failed: ${e}`}));
    }
  }

  document.getElementById("btn-restart").addEventListener("click", ()=> {
    if (!confirm("Restart bot?")) return;
    sendAction("restart_bot");
  });
  document.getElementById("btn-backup").addEventListener("click", ()=> {
    sendAction("trigger_backup");
  });
  document.getElementById("btn-clear").addEventListener("click", ()=> {
    sendAction("clear_cache");
  });

  // Quick actions (placeholders)
  document.getElementById("btn-price").addEventListener("click", ()=> sendAction("refresh_price"));
  document.getElementById("btn-airdrop").addEventListener("click", ()=> sendAction("check_airdrop"));
  document.getElementById("btn-giveaway").addEventListener("click", ()=> sendAction("run_giveaway"));

})();
