$python = 'D:\Mercor\mercor_sprints\sprint_3\.venv\Scripts\pythonw.exe'
$script = 'C:\projetos\smarth-tracker\main.py'
$taskName = 'SmarhtTrackerPonto_Dia25'

schtasks /Create /TN $taskName /TR "`"$python`" `"$script`"" /SC MONTHLY /D 25 /ST 09:00 /F
Write-Host "Tarefa criada: $taskName - Executa todo dia 25 de cada mes as 09:00"
Write-Host "Concluido!"

