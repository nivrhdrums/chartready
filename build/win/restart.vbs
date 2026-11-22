' Restarts ChartReady (stops it quietly, then starts it again). Stops it: by the saved process id, otherwise whatever listens on port 8787 (netstat),
' otherwise any node.exe running server.js.
Set sh = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
dir = fso.GetParentFolderName(WScript.ScriptFullName)
f = dir & "\data\server.pid"
stopped = False

Function Kill(pid)
  Kill = (sh.Run("taskkill /PID " & pid & " /T /F", 0, True) = 0)
End Function

' 1. saved process id
If fso.FileExists(f) Then
  pid = Trim(fso.OpenTextFile(f).ReadAll)
  If pid <> "" Then
    If Kill(pid) Then stopped = True
  End If
  On Error Resume Next
  fso.DeleteFile f
  On Error GoTo 0
End If

' 2. whoever listens on port 8787
If Not stopped Then
  tmp = sh.ExpandEnvironmentStrings("%TEMP%") & "\chartready-ports.txt"
  sh.Run "cmd /c netstat -ano > """ & tmp & """", 0, True
  If fso.FileExists(tmp) Then
    Set t = fso.OpenTextFile(tmp)
    Do Until t.AtEndOfStream
      ln = Trim(Replace(t.ReadLine, vbTab, " "))
      Do While InStr(ln, "  ") > 0
        ln = Replace(ln, "  ", " ")
      Loop
      parts = Split(ln, " ")
      ' listening = local address ends with :8787 and remote address ends with :0 (works in any Windows language)
      If UBound(parts) >= 4 Then
        If Right(parts(1), 5) = ":8787" And Right(parts(2), 2) = ":0" Then
          pid = parts(UBound(parts))
          If IsNumeric(pid) And pid <> "0" Then
            If Kill(pid) Then stopped = True
          End If
        End If
      End If
    Loop
    t.Close
    On Error Resume Next
    fso.DeleteFile tmp
    On Error GoTo 0
  End If
End If

' 3. node.exe running server.js
If Not stopped Then
  On Error Resume Next
  Set wmi = GetObject("winmgmts:\\.\root\cimv2")
  Set ps = wmi.ExecQuery("SELECT ProcessId, CommandLine FROM Win32_Process WHERE Name = 'node.exe'")
  For Each p In ps
    If InStr(LCase(p.CommandLine), "server.js") > 0 Then
      If Kill(p.ProcessId) Then stopped = True
    End If
  Next
  On Error GoTo 0
End If

WScript.Sleep 1000
sh.Run "wscript.exe """ & dir & "\ChartReady.vbs""", 0, False
