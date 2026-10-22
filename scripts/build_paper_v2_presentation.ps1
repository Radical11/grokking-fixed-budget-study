param(
    [string]$RuntimeRoot = (Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies'),
    [string]$PresentationSkill = (Join-Path $env:USERPROFILE '.codex/plugins/cache/openai-primary-runtime/presentations/26.1013.11914/skills/presentations')
)
$ErrorActionPreference='Stop'
$projectRoot=Split-Path $PSScriptRoot -Parent
$pythonExe=Join-Path $projectRoot '.venv/Scripts/python.exe'
$nodeExe=Join-Path $RuntimeRoot 'node/bin/node.exe'
$moduleRoot=Join-Path $RuntimeRoot 'node/node_modules'
foreach($item in @($pythonExe,$nodeExe,$moduleRoot,$PresentationSkill)) {
    if(-not(Test-Path -LiteralPath $item)){throw "Missing presentation dependency: $item"}
}
$buildDir=Join-Path $projectRoot 'tmp/paper_v2_presentation'
New-Item -ItemType Directory -Path $buildDir -Force | Out-Null
$link=Join-Path $buildDir 'node_modules'
if(Test-Path -LiteralPath $link) {
    $existing=Get-Item -LiteralPath $link
    if($existing.LinkType -ne 'Junction' -or [IO.Path]::GetFullPath($existing.Target) -ne [IO.Path]::GetFullPath($moduleRoot)){throw 'Unexpected presentation module link.'}
}else{New-Item -ItemType Junction -Path $link -Target $moduleRoot | Out-Null}
$previousLocation=Get-Location
$priorFilename=$env:DECK_FILENAME;$priorRuntime=$env:CODEX_RUNTIME_DEPENDENCIES;$priorSkill=$env:CODEX_PRESENTATION_SKILL
try {
    Set-Location -LiteralPath $projectRoot
    & $pythonExe presentation/paper_v2_prepare.py
    if($LASTEXITCODE -ne 0){throw 'Presentation preparation failed.'}
    Copy-Item -LiteralPath presentation/paper_v2_build.mjs -Destination (Join-Path $buildDir 'paper_v2_build.mjs') -Force
    Copy-Item -LiteralPath presentation/paper_v2_render.mjs -Destination (Join-Path $buildDir 'paper_v2_render.mjs') -Force
    $env:DECK_FILENAME='presentation_candidate_'+[DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()+'.pptx'
    $env:CODEX_RUNTIME_DEPENDENCIES=$RuntimeRoot;$env:CODEX_PRESENTATION_SKILL=$PresentationSkill
    & $nodeExe (Join-Path $buildDir 'paper_v2_build.mjs')
    if($LASTEXITCODE -ne 0){throw 'Presentation authoring/validation failed.'}
    $candidate=Join-Path $projectRoot ('output/paper_v2/'+$env:DECK_FILENAME)
    $saved=Join-Path $buildDir $env:DECK_FILENAME
    Move-Item -LiteralPath $candidate -Destination $saved
    Copy-Item -LiteralPath $saved -Destination output/paper_v2/presentation.pptx -Force
    & $nodeExe (Join-Path $buildDir 'paper_v2_render.mjs')
    if($LASTEXITCODE -ne 0){throw 'Final presentation reimport failed.'}
    & $pythonExe presentation/paper_v2_pdf.py
    if($LASTEXITCODE -ne 0){throw 'Matching presentation PDF failed.'}
}finally{
    $env:DECK_FILENAME=$priorFilename;$env:CODEX_RUNTIME_DEPENDENCIES=$priorRuntime;$env:CODEX_PRESENTATION_SKILL=$priorSkill
    Set-Location -LiteralPath $previousLocation
}
