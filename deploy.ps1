[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

param([string]$msg = "update")

Write-Host ""
Write-Host "🎹 Deploying Teach Me Music..." -ForegroundColor Cyan
Write-Host ""

# Add all changes
git add .
Write-Host "✅ Files staged" -ForegroundColor Green

# Commit
git commit -m $msg
Write-Host "✅ Committed: $msg" -ForegroundColor Green

# Push
git push origin main
Write-Host ""
Write-Host "🎉 Deployed successfully!" -ForegroundColor Green
Write-Host "🌍 GitHub: https://github.com/shmouel1824/teach-me-music" -ForegroundColor Cyan
Write-Host ""
