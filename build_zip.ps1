# ===================================================================
#  🚀 WENBNB Neural Engine v5.0 — Build ZIP Script (PowerShell)
#  Safely packages your project into a deploy-ready ZIP archive.
#  Author: WENBNB Neural Cloud Systems
#  Date: 2025
# ===================================================================

param(
    [string]$version = "v1.0",
    [string]$outdir = ".\dist"
)

$projName = "WENBNB_Bot"
$zipName = "$projName`_$version.zip"
$staging = "$env:TEMP\$projName-staging"

# 🧹 Clean staging folder
if (Test-Path $staging) { Remove-Item $staging -Recurse -Force }

# 📂 Directories and files to include in build
$include = @(
    "main.py",
    "wenbot.py",
    "README.md",
    "LICENSE",
    "requirements.txt",
    ".env.example",
    "core",
    "plugins",
    "dashboard",
    "assets",
    "docs"
)

Write-Host "`n📦 Preparing WENBNB AI Build v$version ..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path $staging | Out-Null

# 🧩 Copy project files
foreach ($item in $include) {
    if (Test-Path $item) {
        Copy-Item $item -Recurse -Force -Destination $staging
        Write-Host "✅ Included: $item"
    } else {
        Write-Host "⚠️ Skipped (not found): $item" -ForegroundColor Yellow
    }
}

# 🚫 Remove any sensitive files just in case
$maybeSecrets = @(".env", "emotion_state.json", "giveaway_data.json", "__pycache__", "*.pyc")
foreach ($s in $maybeSecrets) {
    Get-ChildItem -Path $staging -Recurse -Filter $s -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
}

# 📁 Create output directory
if (!(Test-Path $outdir)) { New-Item -ItemType Directory -Path $outdir | Out-Null }

# 🗜️ Create the ZIP archive
$zipPath = Join-Path $outdir $zipName
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }

Write-Host "`n🧠 Compressing project files..." -ForegroundColor Cyan
Compress-Archive -Path (Join-Path $staging "*") -DestinationPath $zipPath -Force

# 🔐 Generate SHA256 checksum
$sha = Get-FileHash -Algorithm SHA256 $zipPath
$shaStr = $sha.Hash
$shaFile = "$zipPath.sha256"
Set-Content -Path $shaFile -Value $shaStr

# 🧹 Clean up
Remove-Item $staging -Recurse -Force

# ✅ Done
Write-Host "`n🎉 Build complete!" -ForegroundColor Green
Write-Host "📁 ZIP saved to: $zipPath"
Write-Host "🔑 SHA256 checksum saved to: $shaFile"
Write-Host '🚀 Powered by WENBNB Neural Engine — AI Core Intelligence 24x7' -ForegroundColor Cyan

