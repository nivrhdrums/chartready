' Stops ChartReady: first by the saved process id, otherwise whatever is listening on port 8787.
Set sh = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
dir = fso.GetParentFolderName(WScript.ScriptFullName)
f = dir & "\data\server.pid"
stopped = False
If fso.FileExists(f) Then
  pid = Trim(fso.OpenTextFile(f).ReadAll)
  If pid <> "" Then
    If sh.Run("taskkill /PID " & pid & " /T /F", 0, True) = 0 Then stopped = True
  End If
  On Error Resume Next
  fso.DeleteFile f
  On Error GoTo 0
End If
If Not stopped Then
  ps = "$p = Get-NetTCPConnection -LocalPort 8787 -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique; " & _
       "if ($p) { $p | ForEach-Object { taskkill /PID $_ /T /F | Out-Null }; exit 0 } else { exit 1 }"
  If sh.Run("powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -Command """ & ps & """", 0, True) = 0 Then stopped = True
End If
If stopped Then
  MsgBox "ChartReady כובה.", 64, "ChartReady"
Else
  MsgBox "ChartReady לא פועל כרגע.", 64, "ChartReady"
End If
