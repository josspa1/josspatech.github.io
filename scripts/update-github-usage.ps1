# Updates admin/shared/github-usage.json using git count-objects -vH (no GitHub API token).
# Usage: .\scripts\update-github-usage.ps1
param(
  [string]$SiteRepo = "$env:USERPROFILE\Documents\GitHub\josspatech.github.io",
  [string]$PbjRepo  = "$env:USERPROFILE\Documents\GitHub\PocketBudJet",
  [string]$OutputJson = "$PSScriptRoot\..\admin\shared\github-usage.json"
)

function Get-PackSizeMB {
  param([string]$RepoPath)
  if (-not (Test-Path (Join-Path $RepoPath ".git"))) {
    Write-Warning "Not a git repo: $RepoPath"
    return $null
  }
  Push-Location $RepoPath
  try {
    $out = git count-objects -vH 2>$null
    if ($LASTEXITCODE -ne 0) { return $null }
    $line = $out | Where-Object { $_ -match '^size-pack:' } | Select-Object -First 1
    if (-not $line) { return $null }
    if ($line -match '([\d.]+)\s*MiB') { return [math]::Round([double]$Matches[1], 0) }
    if ($line -match '([\d.]+)\s*GiB') { return [math]::Round([double]$Matches[1] * 1024, 0) }
    if ($line -match '([\d.]+)\s*KiB') { return [math]::Round([double]$Matches[1] / 1024, 0) }
    return $null
  } finally {
    Pop-Location
  }
}

$siteMB = Get-PackSizeMB -RepoPath $SiteRepo
$pbjMB  = Get-PackSizeMB -RepoPath $PbjRepo

if ($null -eq $siteMB -and $null -eq $pbjMB) {
  Write-Error "Could not read pack sizes. Check repo paths: SiteRepo=$SiteRepo PbjRepo=$PbjRepo"
  exit 1
}

$repos = @(
  @{ name = "josspatech.github.io"; label = "Website (GitHub Pages)"; sizeMB = $(if ($null -ne $siteMB) { $siteMB } else { 0 }) },
  @{ name = "PocketBudJet";          label = "PBJ app source";         sizeMB = $(if ($null -ne $pbjMB) { $pbjMB } else { 0 }) }
)
$total = ($repos | ForEach-Object { $_.sizeMB } | Measure-Object -Sum).Sum

$payload = [ordered]@{
  asOf    = (Get-Date).ToString("yyyy-MM-dd")
  totalMB = $total
  note    = "run scripts/update-github-usage.ps1 to refresh"
  repos   = $repos
}

$json = ($payload | ConvertTo-Json -Depth 4)
Set-Content -Path $OutputJson -Value $json -Encoding UTF8
Write-Host "Wrote $OutputJson — total ${total}MB (site=$siteMB, pbj=$pbjMB)"
