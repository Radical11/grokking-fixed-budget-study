param(
    [string]$RuntimeRoot = (Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies'),
    [string]$PresentationSkill = (Join-Path $env:USERPROFILE '.codex/plugins/cache/openai-primary-runtime/presentations/26.1013.11914/skills/presentations')
)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$pythonExe = Join-Path $projectRoot '.venv/Scripts/python.exe'
$nodeExe = Join-Path $RuntimeRoot 'node/bin/node.exe'
$moduleRoot = Join-Path $RuntimeRoot 'node/node_modules'
foreach ($required in @($pythonExe, $nodeExe, $moduleRoot, $PresentationSkill)) {
    if (-not (Test-Path -LiteralPath $required)) { throw "Required presentation dependency is missing: $required" }
}
$buildDir = Join-Path $projectRoot 'tmp/final_presentation'
New-Item -ItemType Directory -Path $buildDir -Force | Out-Null
$link = Join-Path $buildDir 'node_modules'
if (Test-Path -LiteralPath $link) {
    $existing = Get-Item -LiteralPath $link
    if ($existing.LinkType -ne 'Junction' -or [IO.Path]::GetFullPath($existing.Target) -ne [IO.Path]::GetFullPath($moduleRoot)) {
        throw "Unexpected node_modules location: $link"
    }
} else { New-Item -ItemType Junction -Path $link -Target $moduleRoot | Out-Null }
$previousLocation = Get-Location
$priorFilename = $env:DECK_FILENAME
$priorRuntime = $env:CODEX_RUNTIME_DEPENDENCIES
$priorSkill = $env:CODEX_PRESENTATION_SKILL
try {
    Set-Location -LiteralPath $projectRoot
    & $pythonExe presentation/final_prepare.py
    if ($LASTEXITCODE -ne 0) { throw 'Presentation evidence preparation failed.' }
    Copy-Item -LiteralPath presentation/final_build.mjs -Destination (Join-Path $buildDir 'final_build.mjs') -Force
    Copy-Item -LiteralPath presentation/final_render.mjs -Destination (Join-Path $buildDir 'final_render.mjs') -Force
    $env:DECK_FILENAME = 'final_presentation_candidate_' + [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds() + '.pptx'
    $env:CODEX_RUNTIME_DEPENDENCIES = $RuntimeRoot
    $env:CODEX_PRESENTATION_SKILL = $PresentationSkill
    & $nodeExe (Join-Path $buildDir 'final_build.mjs')
    if ($LASTEXITCODE -ne 0) { throw 'Editable presentation generation or validation failed.' }
    $candidate = Join-Path $projectRoot ('output/final_package/' + $env:DECK_FILENAME)
    $savedCandidate = Join-Path $buildDir $env:DECK_FILENAME
    Move-Item -LiteralPath $candidate -Destination $savedCandidate
    Copy-Item -LiteralPath $savedCandidate -Destination output/final_package/final_presentation.pptx -Force
    & $nodeExe (Join-Path $buildDir 'final_render.mjs')
    if ($LASTEXITCODE -ne 0) { throw 'Final PPTX import/render failed.' }
    foreach ($step in @('presentation/final_export_pdf.py', 'presentation/final_originality_screen.py', 'presentation/final_verify.py')) {
        & $pythonExe $step
        if ($LASTEXITCODE -ne 0) { throw "Final package step failed: $step" }
    }
    & $pythonExe scripts/final_manifest.py --write
    if ($LASTEXITCODE -ne 0) { throw 'Package provenance generation failed.' }
} finally {
    $env:DECK_FILENAME = $priorFilename
    $env:CODEX_RUNTIME_DEPENDENCIES = $priorRuntime
    $env:CODEX_PRESENTATION_SKILL = $priorSkill
    Set-Location -LiteralPath $previousLocation
}
