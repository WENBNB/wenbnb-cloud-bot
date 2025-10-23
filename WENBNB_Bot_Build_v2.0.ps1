# 🌐 WENBNB AI BOT BUILD SCRIPT v2.0
# 💫 Powered by WENBNB Neural Engine — Emotional AI Integration v4.1
# 👑 Auto-packs latest bot files into a signed ZIP

# Step 1: Define paths
$sourcePath = "C:\Users\YourUserName\Desktop\wenbnb"     # 👈 CHANGE this to your project folder path
$buildPath  = "C:\Users\YourUserName\Desktop\WENBNB_Builds"  # 👈 Where ZIP file will be saved
$timestamp  = Get-Date -Format "yyyyMMdd_HHmmss"
$zipName    = "WENBNB_AI_Bot_v2.0_$timestamp.zip"
$zipPath    = Join-Path $buildPath $zipName

# Step 2: Check folder existence
if (-Not (Test-Path $sourcePath)) {
    Write-Host "❌ Source folder not found: $sourcePath"
    exit
}
if (-Not (Test-Path $buildPath)) {
    New-Item -ItemType Directory -Path $buildPath | Out-Null
    Write-Host "📂 Created build directory: $buildPath"
}

# Step 3: Create ZIP archive
try {
    Compress-Archive -Path "$sourcePath\*" -DestinationPath $zipPath -Force
    Write-Host "✅ Successfully created ZIP build at:`n$zipPath"
} catch {
    Write-Host "⚠️ Error creating ZIP file: $($_.Exception.Message)"
    exit
}

# Step 4: Generate SHA256 signature
$hash = (Get-FileHash -Path $zipPath -Algorithm SHA256).Hash
$hashFile = $zipPath + ".sha256"
$hash | Out-File -FilePath $hashFile -Encoding ascii

# Step 5: Done message
Write-Host "`n🚀 Build Completed Successfully!"
Write-Host "📦 File: $zipName"
Write-Host "🔐 Signature: $hashFile"
Write-Host "💫 Powered by WENBNB Neural Engine — Emotional AI Integration v4.1"
