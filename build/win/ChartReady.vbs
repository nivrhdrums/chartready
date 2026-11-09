' Starts ChartReady in the background (no window) and opens it in the browser.
' Add any argument (the startup shortcut passes "quiet") to start without opening the browser.
Set sh = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
dir = fso.GetParentFolderName(WScript.ScriptFullName)
quiet = (WScript.Arguments.Count > 0)
running = False
On Error Resume Next
Set x = CreateObject("MSXML2.ServerXMLHTTP")
x.setTimeouts 500, 500, 500, 500
x.open "GET", "http://localhost:8787/lan", False
x.send
If Err.Number = 0 Then
  If x.status = 200 Then running = True
End If
On Error GoTo 0
If Not running Then
  If sh.Run("cmd /c where node", 0, True) <> 0 Then
    MsgBox "צריך להתקין Node.js מ- nodejs.org (פעם אחת) ואז להפעיל שוב.", 48, "ChartReady"
    WScript.Quit
  End If
  If Not fso.FolderExists(dir & "\data") Then fso.CreateFolder(dir & "\data")
  sh.CurrentDirectory = dir
  sh.Environment("Process")("LOCAL") = "1"
  sh.Run "cmd /c node server.js > data\server.log 2>&1", 0, False
  WScript.Sleep 1500
End If
' first run: a ChartReady icon on the desktop
lnk = sh.SpecialFolders("Desktop") & "\ChartReady.lnk"
If Not fso.FileExists(lnk) Then
  Set l = sh.CreateShortcut(lnk)
  l.TargetPath = "wscript.exe"
  l.Arguments = Chr(34) & dir & "\ChartReady.vbs" & Chr(34)
  l.WorkingDirectory = dir
  l.IconLocation = dir & "\chartready.ico"
  l.Description = "ChartReady"
  l.Save
End If
' open as its own app window (Edge app mode, own profile so sound is allowed without a click)
If Not quiet Then
  prof = sh.ExpandEnvironmentStrings("%LOCALAPPDATA%") & "\ChartReadyApp"
  args = "--app=http://localhost:8787 --user-data-dir=" & Chr(34) & prof & Chr(34) & " --autoplay-policy=no-user-gesture-required --no-first-run --window-size=1280,820"
  r = sh.Run("cmd /c start """" msedge " & args, 0, False)
End If
