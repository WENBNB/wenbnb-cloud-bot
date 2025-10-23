# ==========================================
# 🚀 WENBNB Neural Engine v5.0 — Auto Redeploy Script
# Automates GitHub commit + Render rebuild
# ==========================================

# --- CONFIGURATION ---
$repoPath = "F:\WENBNB"          # ⚠️ change this to your repo path
$commitMsg = "🧠 Auto update & redeploy via AI Core"
$renderServiceName = "wenbnb-neural-engine"  # must match 'render.yaml' service name

# --- STEP 1: GIT COMMIT & PUSH ---
Write-Host "📦 Committing & pushing changes to GitHub..." -ForegroundColor Cyan
Set-Location $repoPath
git add .
git commit -m "$commitMsg"
git push origin main

# --- STEP 2: RENDER DEPLOY TRIGGER ---
Write-Host "⚙️ Triggering Render redeploy..." -ForegroundColor Cyan
$deployHookUrl = Read-Host "Enter your Render Deploy Hook URL (once)"
if (-not $deployHookUrl) {
    Write-Host "❌ No deploy hook provided — skipping auto-redeploy."
} else {
    Invoke-WebRequest -Uri $deployHookUrl -Method POST | Out-Null
    Write-Host "✅ Redeploy triggered successfully!" -ForegroundColor Green
}

Write-Host "`n✨ WENBNB Neural Engine — Auto Sync Complete! ✨" -ForegroundColor Magenta
