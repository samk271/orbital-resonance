Set objShell = CreateObject("WScript.Shell")
objShell.Run """" & WScript.ScriptFullName & "\..\start venv.bat""" & " """ & WScript.Arguments(0) & """", 0, True
