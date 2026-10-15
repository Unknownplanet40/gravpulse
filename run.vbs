Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
strDir = fso.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = strDir

pythonExe = "C:\Python312\pythonw.exe"
If Not fso.FileExists(pythonExe) Then
    pythonExe = "pythonw.exe"
End If

WshShell.Run """" & pythonExe & """ """ & strDir & "\main.pyw""", 0, False
