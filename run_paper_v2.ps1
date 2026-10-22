param([switch]$AnalysisOnly,[switch]$Status,[int]$Workers=3,[int]$WaitForCalibrationPid=0)
$ErrorActionPreference='Stop'
Set-Location -LiteralPath $PSScriptRoot
$pythonExe=Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
$dataDir=Join-Path $PSScriptRoot 'data/paper_v2'
if($Status){
    foreach($name in @('status.json','pipeline_status.json','session_progress.json')){
        $file=Join-Path $dataDir $name
        if(Test-Path -LiteralPath $file){Get-Content -LiteralPath $file}
    }
    exit 0
}
if($Workers -lt 1 -or $Workers -gt 3){throw 'Workers must be between one and three.'}
New-Item -ItemType Directory -Path $dataDir -Force | Out-Null
$lockPath=Join-Path $dataDir '.pipeline.lock'
$runnerLock=[IO.File]::Open($lockPath,[IO.FileMode]::OpenOrCreate,[IO.FileAccess]::ReadWrite,[IO.FileShare]::None)
$priorLC=$env:LC_ALL;$priorLang=$env:LANG
function Set-PipelineStage([string]$stage){
    @{stage=$stage;pid=$PID;updated_at_utc=[DateTimeOffset]::UtcNow.ToString('o');analysis_only=[bool]$AnalysisOnly} |
        ConvertTo-Json | Set-Content -LiteralPath (Join-Path $dataDir 'pipeline_status.json') -Encoding utf8
    Write-Output ('PIPELINE '+$stage)
}
function Invoke-PythonStep([string[]]$stepArgs){
    & $pythonExe @stepArgs
    if($LASTEXITCODE -ne 0){throw ('Python step failed: '+($stepArgs -join ' '))}
}
try{
    $env:LC_ALL='C';$env:LANG='C'
    if(-not $AnalysisOnly){
        if($WaitForCalibrationPid -gt 0){
            Set-PipelineStage 'waiting_for_existing_calibration'
            Wait-Process -Id $WaitForCalibrationPid -ErrorAction SilentlyContinue
        }else{
            $active=Join-Path $dataDir 'active_phase.json'
            if(Test-Path -LiteralPath $active){
                $record=Get-Content -LiteralPath $active -Raw | ConvertFrom-Json
                if(Get-Process -Id $record.pid -ErrorAction SilentlyContinue){throw 'Another training parent is active. Wait for it; do not run the same study twice.'}
            }
        }
        Set-PipelineStage 'calibration'
        Invoke-PythonStep -stepArgs @('-u','-m','grokking.paper_study','calibrate','--workers',"$Workers")
        Set-PipelineStage 'freezing_predictions'
        Invoke-PythonStep -stepArgs @('-m','grokking.paper_study','freeze')
        Set-PipelineStage 'validation'
        Invoke-PythonStep -stepArgs @('-u','-m','grokking.paper_study','validate','--workers',"$Workers")
    }
    Set-PipelineStage 'export_and_tests'
    Invoke-PythonStep -stepArgs @('-m','grokking.paper_study','export')
    Invoke-PythonStep -stepArgs @('-m','pytest','-q')
    Set-PipelineStage 'R_analysis'
    $rscript=Join-Path $PSScriptRoot '.tools/R/app/bin/Rscript.exe'
    if(-not(Test-Path -LiteralPath $rscript)){$rscript=(Get-Command Rscript -ErrorAction Stop).Source}
    & $rscript analysis/paper_v2.R
    if($LASTEXITCODE -ne 0){throw 'Base-R follow-up analysis failed.'}
    Set-PipelineStage 'raw_trace_audit'
    Invoke-PythonStep -stepArgs @('-m','grokking.paper_audit')
    Set-PipelineStage 'paper_and_supplement'
    Invoke-PythonStep -stepArgs @('-m','grokking.paper_report')
    Set-PipelineStage 'editable_presentation'
    & (Join-Path $PSScriptRoot 'scripts/build_paper_v2_presentation.ps1')
    Set-PipelineStage 'source_screen'
    Invoke-PythonStep -stepArgs @('-m','grokking.paper_sources')
    Set-PipelineStage 'independent_reproduction'
    Invoke-PythonStep -stepArgs @('-m','grokking.paper_verify','--reproduce')
    Set-PipelineStage 'awaiting_visual_review'
}catch{
    Set-PipelineStage 'needs_attention'
    $_ | Out-String | Set-Content -LiteralPath (Join-Path $dataDir 'pipeline_error.txt') -Encoding utf8
    throw
}finally{
    $runnerLock.Dispose();$env:LC_ALL=$priorLC;$env:LANG=$priorLang
}
