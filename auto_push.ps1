# auto_push.ps1
# Simple Git automation script for AutoDev updates

# Navigate to project folder
Set-Location "C:\Users\USER\SynapseChamber"

# Stage all changes
git add .

# Create timestamped commit message
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$commitMessage = "AutoDev update - $timestamp"

# Commit changes (if any)
git commit -m "$commitMessage"

# Push to GitHub
git push origin main

# Done message
Write-Host "✅ Auto-push complete at $timestamp"
