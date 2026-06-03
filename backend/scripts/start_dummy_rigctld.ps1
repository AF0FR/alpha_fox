$RigModel = 1
$Port = 4532

Write-Host "Starting Hamlib dummy rigctld..."
Write-Host "Model: $RigModel"
Write-Host "Port:  $Port"

$rigctld = Get-Command rigctld -ErrorAction SilentlyContinue

if (-not $rigctld) {
    Write-Host ""
    Write-Host "rigctld was not found in PATH."
    Write-Host "Install Hamlib / rigctld first, then rerun this script."
    exit 1
}

rigctld -m $RigModel -t $Port
