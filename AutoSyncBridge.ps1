# ======================================
# 🔁 AutoSyncBridge v1.0 for SynapseChamber Sandbox
# ======================================

param (
    [string]$RepoPath = "C:\\Users\\Vincent\\SynapseChamberSandbox",
    [string]$BranchName = "sandbox",
    [string]$BackupPath = "C:\\Users\\Vincent\\SynapseChamberBackups"
)

# Ensure directories exist
if (!(Test-Path $RepoPath)) { Write-Host "❌ Repo path not found: $RepoPath"; exit }
if (!(Test-Path $BackupPath)) { New-Item -ItemType Directory -Path $BackupPath | Out-Null }

# Load config file
$configFile = Join-Path $RepoPath ".githubconfig.json"
if (!(Test-Path $configFile)) { Write-Host "❌ Missing .githubconfig.json"; exit }

$config = Get-Content $configFile | ConvertFrom-Json
$Token = (Get-Item env:$($config.token_env)).Value
if (-not $Token) { Write-Host "⚠️ GITHUB_TOKEN not found in environment"; exit }

# Set up Git
Set-Location $RepoPath
git fetch origin $BranchName
git checkout $BranchName

Write-Host "🔄 Watching $RepoPath for changes..."
$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $RepoPath
$watcher.IncludeSubdirectories = $true
$watcher.EnableRaisingEvents = $true

$onChange = {
    Start-Sleep -Seconds 5  # debounce multiple quick events

    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupDir = Join-Path $BackupPath "Backup_$timestamp"

    # Create backup
    Copy-Item -Path $RepoPath -Destination $backupDir -Recurse -Force
    Write-Host "📦 Backup created at: $backupDir"

    # Stage, commit, push
    git add .
    git commit -m "AutoSyncBridge update at $timestamp"
    git push origin $BranchName

    Write-Host "✅ Changes synced to GitHub ($BranchName branch) at $timestamp"
}

# Hook up watcher events
Register-ObjectEvent $watcher Changed -Action $onChange
Register-ObjectEvent $watcher Created -Action $onChange
Register-ObjectEvent $watcher Deleted -Action $onChange
Register-ObjectEvent $watcher Renamed -Action $onChange

# Keep running until manually stopped
while ($true) { Start-Sleep -Seconds 60 }
