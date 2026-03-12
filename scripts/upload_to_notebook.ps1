# Batch upload script for NotebookLM sources
$CLI = "C:\Users\bizca\AppData\Local\Programs\Python\Python313\Scripts\notebooklm.exe"

# 1. Retry failed March log
& $CLI source add "PromptTracking\Session Log 20260303.md" --title "Session Log 20260303"

# 2. Add the 8-Part Series
$files = Get-ChildItem "docs\Self-Improvement" -Filter "Part_*.md"
foreach ($file in $files) {
    Write-Host "Adding $($file.Name)..."
    & $CLI source add $file.FullName --title $file.BaseName
}

# 3. Add other core docs
& $CLI source add "docs\7 levels of memory.md" --title "7 Levels of Memory"
& $CLI source add "PROSPECTIVE_MEMORY_INTEGRATION.md" --title "Prospective Memory Plan"
