# ======================================
# AutoDev Bi-Directional Sync Script v2
# Logs all activity to sync_log.txt
# ======================================

# Force UTF-8 encoding (just in case)
chcp 65001 | Out-Null
$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::UTF8

# Paths
$repoPath = "C:\Users\USER\SynapseChamber"
$logFile = "$repoPath\sync_log.txt"
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

# Helper for logging
function Log {
    param([string]$message)
    $entry = "[$timestamp] $message"
    Add-Content -Path $logFile -Value $entry
    Write-Host $message
}

# Go to repo
Set-Location $repoPath

Log "🚀 Starting AutoDev bi-directional sync."

# Step 1: Pull latest from GitHub
git pull origin main 2>&1 | Tee-Object -Variable pullOutput | Out-Null
Log "⬇️ Pull result: $pullOutput"

# Step 2: Stage local changes
git add -A
Log "📦 Staged all changes."

# Step 3: Commit local changes
$commitMessage = "Auto-sync — $timestamp"
$commitResult = git commit -m "$commitMessage" 2>&1
if ($commitResult -match "nothing to commit") {
    Log "🟢 Nothing to commit — repo is already up to date."
} else {
    Log "📝 Commit result: $commitResult"
}

# Step 4: Push changes
$pushResult = git push origin main 2>&1
Log "⬆️ Push result: $pushResult"

# Step 5: Completion message
Log "✅ Bi-directional sync complete at $timestamp"
