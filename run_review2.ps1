$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
& '.\.venv\Scripts\python.exe' -m grokking.study review2
if ($LASTEXITCODE -ne 0) { throw 'Main-study expansion failed.' }
& '.\.venv\Scripts\python.exe' -m grokking.study validation
if ($LASTEXITCODE -ne 0) { throw 'Fresh-seed validation failed.' }
$taskR = Join-Path $PSScriptRoot '.tools\R\app\bin\Rscript.exe'
if (-not (Test-Path -LiteralPath $taskR)) { $taskR = (Get-Command Rscript -ErrorAction Stop).Source }
& $taskR analysis/analyze.R review2
if ($LASTEXITCODE -ne 0) { throw 'R analysis failed.' }
& '.\.venv\Scripts\python.exe' -m grokking.audit review2
if ($LASTEXITCODE -ne 0) { throw 'Raw trace or analysis audit failed.' }
& '.\.venv\Scripts\python.exe' -m grokking.report review2
if ($LASTEXITCODE -ne 0) { throw 'Report generation failed.' }
