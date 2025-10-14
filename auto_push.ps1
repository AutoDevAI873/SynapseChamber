# ===============================
# Auto Git Push Script (SynapseChamber)
# ===============================

# Navigate to repo directory
Set-Location -Path "C:\Users\USER\SynapseChamber"

# Add all changed files
git add -A

# Create a timestamp for commit message
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$commitMessage = "AutoDev update — $timestamp"

# Commit changes (if any)
git commit -m "$commitMessage"

# Push to GitHub
git push origin main

Write-Host "✅ Auto-push complete at $timestamp"
