$connections = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue

if (-not $connections) {
    Write-Host "No process is listening on port 8000."
    exit 0
}

foreach ($connection in $connections) {
    $pidToKill = $connection.OwningProcess
    Write-Host "Killing process $pidToKill on port 8000..."
    Stop-Process -Id $pidToKill -Force
}

Write-Host "Port 8000 cleared."