$taskName = 'SmarhtTrackerPonto_Dia25'

schtasks /Delete /TN $taskName /F
Write-Host "Tarefa '$taskName' removida."

