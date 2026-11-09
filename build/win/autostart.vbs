Set sh = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
dir = fso.GetParentFolderName(WScript.ScriptFullName)
lnkPath = sh.SpecialFolders("Startup") & "\ChartReady.lnk"
If fso.FileExists(lnkPath) Then
  fso.DeleteFile lnkPath
  MsgBox "ההפעלה האוטומטית בוטלה.", 64, "ChartReady"
Else
  Set l = sh.CreateShortcut(lnkPath)
  l.TargetPath = "wscript.exe"
  l.Arguments = Chr(34) & dir & "\ChartReady.vbs" & Chr(34) & " quiet"
  l.WorkingDirectory = dir
  l.Save
  MsgBox "מעכשיו ChartReady יופעל ברקע בכל הדלקה של המחשב." & vbCrLf & "להפעיל את הקובץ הזה שוב = ביטול.", 64, "ChartReady"
End If
