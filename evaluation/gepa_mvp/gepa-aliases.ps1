# GEPA MVP helper aliases
# Usage: . .\evaluation\gepa_mvp\gepa-aliases.ps1

function gepa-run {
    & "$PSScriptRoot\gepa-run.ps1" @args
}

function Show-GepaHelp {
    Write-Host "GEPA MVP Commands:" -ForegroundColor Green
    Write-Host "  gepa-run  - Run GEPA trial logger wrapper" -ForegroundColor Yellow
    Write-Host "" 
    Write-Host "Example:" -ForegroundColor Green
    Write-Host "  gepa-run -PromptId prompt_v1 -Model claude-sonnet-4.5 -GepaScore 0.8 -PassFail pass -PromptFile .\evaluation\gepa_mvp\samples\prompt.txt -ResponseFile .\evaluation\gepa_mvp\samples\response.txt" -ForegroundColor Cyan
}

Set-Alias -Name gepa-help -Value Show-GepaHelp -Force
