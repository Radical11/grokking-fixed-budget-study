$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
& '.\.venv\Scripts\python.exe' -m grokking.study review1
if ($LASTEXITCODE -ne 0) { throw 'Training or pilot failed; review the preserved error evidence.' }
$taskR = Join-Path $PSScriptRoot '.tools\R\app\bin\Rscript.exe'
if (-not (Test-Path -LiteralPath $taskR)) { $taskR = (Get-Command Rscript -ErrorAction Stop).Source }
& $taskR analysis/analyze.R review1
if ($LASTEXITCODE -ne 0) { throw 'R analysis failed.' }
& '.\.venv\Scripts\python.exe' -m grokking.audit review1
if ($LASTEXITCODE -ne 0) { throw 'Raw trace or analysis audit failed.' }
& '.\.venv\Scripts\python.exe' -m grokking.report review1
if ($LASTEXITCODE -ne 0) { throw 'Report generation failed.' }
