$root = 'C:\Users\jossp\Documents\GitHub\josspatech.github.io\videos'
$issues = @()
Get-ChildItem -Path $root -Recurse -Filter 'index.html' | ForEach-Object {
  $dir = $_.DirectoryName
  $rel = $dir.Replace('C:\Users\jossp\Documents\GitHub\josspatech.github.io\', '')
  $content = Get-Content $_.FullName -Raw
  $matches = [regex]::Matches($content, "audio/slide-\d+\.mp3")
  $paths = $matches | ForEach-Object { $_.Value } | Select-Object -Unique
  foreach ($p in $paths) {
    $full = Join-Path $dir ($p -replace '/', '\')
    if (-not (Test-Path $full)) {
      $issues += [pscustomobject]@{ Video=$rel; Issue='MISSING'; File=$p; Bytes=$null }
    } else {
      $len = (Get-Item $full).Length
      if ($len -eq 0) {
        $issues += [pscustomobject]@{ Video=$rel; Issue='ZERO_BYTE'; File=$p; Bytes=0 }
      } elseif ($len -lt 5000) {
        $issues += [pscustomobject]@{ Video=$rel; Issue='SMALL'; File=$p; Bytes=$len }
      }
    }
  }
}
$issues | Format-Table -AutoSize
Write-Host "Total issues: $($issues.Count)"
