Set sh = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
dir = fso.GetParentFolderName(WScript.ScriptFullName)
f = dir & "\data\server.pid"
If fso.FileExists(f) Then
  pid = Trim(fso.OpenTextFile(f).ReadAll)
  sh.Run "taskkill /PID " & pid & " /T /F", 0, True
  fso.DeleteFile f
  MsgBox "ChartReady כובה.", 64, "ChartReady"
Else
  MsgBox "ChartReady לא פועל כרגע.", 64, "ChartReady"
End If
