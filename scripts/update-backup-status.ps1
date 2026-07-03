# Updates admin/shared/backup-status.json from a local HHH backup zip.
# Usage:
#   .\scripts\update-backup-status.ps1
#   .\scripts\update-backup-status.ps1 -ZipPath "D:\Backups\HHH-backup-2026-07-03.zip"
param(
  [string]$ZipPath = "",
  [string]$SearchDir = "$env:USERPROFILE\Documents\MobileApps\HHH\Backups",
  [string]$OutputJson = "$PSScriptRoot\..\admin\shared\backup-status.json"
)

function Find-LatestBackup {
  param([string]$Dir)
  if (-not (Test-Path $Dir)) { return $null }
  Get-ChildItem -Path $Dir -Filter "HHH-backup-*.zip" -File |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
}

if ($ZipPath) {
  $file = Get-Item -LiteralPath $ZipPath -ErrorAction SilentlyContinue
} else {
  $file = Find-LatestBackup -Dir $SearchDir
}

if (-not $file) {
  Write-Error "No HHH-backup-*.zip found. Pass -ZipPath or place backups in $SearchDir"
  exit 1
}

$sizeMB = [math]::Round($file.Length / 1MB, 0)
$payload = [ordered]@{
  lastHHHBackup = $file.Name
  path          = $file.FullName
  sizeMB        = $sizeMB
  updatedAt     = (Get-Date).ToString("o")
  note          = "Static JSON · no cloud cost — run scripts/update-backup-status.ps1 or edit manually"
}

$json = ($payload | ConvertTo-Json -Depth 4)
Set-Content -Path $OutputJson -Value $json -Encoding UTF8
Write-Host "Wrote $OutputJson — $($file.Name) ($sizeMB MB)"
