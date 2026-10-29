Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
strDir = fso.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = strDir

exePath = strDir & "\GravPulse.exe"
If Not fso.FileExists(exePath) Then
    exePath = strDir & "\dist\GravPulse.exe"
End If

If fso.FileExists(exePath) Then
    WshShell.Run """" & exePath & """", 0, False
Else
    pythonExe = "C:\Python312\pythonw.exe"
    If Not fso.FileExists(pythonExe) Then
        pythonExe = "pythonw.exe"
    End If
    WshShell.Run """" & pythonExe & """ """ & strDir & "\main.pyw""", 0, False
End If
