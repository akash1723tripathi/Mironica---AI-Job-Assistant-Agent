# Daily Automation Guide (Windows Task Scheduler)

The AI Job Assistant is configured to run automatically every day at 11:00 AM IST.

## Setting Up Windows Task Scheduler

### Option 1: PowerShell Command (Recommended)

Run PowerShell as Administrator and execute:

```powershell
$Action = New-ScheduledTaskAction -Execute "python.exe" -Argument "d:\codes\Projects\AI Job Assistant\src\run_pipeline.py" -WorkingDirectory "d:\codes\Projects\AI Job Assistant"
$Trigger = New-ScheduledTaskTrigger -Daily -At 11:00AM
Register-ScheduledTask -TaskName "AI_Job_Assistant_Daily" -Action $Action -Trigger $Trigger -Description "Daily AI Job Assistant Discovery & Notification Pipeline"
```

### Option 2: GUI Setup

1. Open **Task Scheduler** (`taskschd.msc`).
2. Click **Create Basic Task...**
3. Name: `AI_Job_Assistant_Daily`
4. Trigger: **Daily** at `11:00 AM`.
5. Action: **Start a program**
   - Program/script: `python.exe`
   - Add arguments: `src/run_pipeline.py`
   - Start in: `D:\codes\Projects\AI Job Assistant`
6. Click Finish.

## Execution Verification

Check execution reports at:
- `data/reports/run_report.json`
- `data/reports/quality_report.md`
