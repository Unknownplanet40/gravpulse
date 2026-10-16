import os
import sys
import subprocess
from pathlib import Path

STARTUP_NAME = "GravPulse.lnk"

def get_startup_dir() -> Path:
    appdata = os.environ.get("APPDATA")
    if not appdata:
        appdata = os.path.expanduser("~\\AppData\\Roaming")
    return Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"

def get_startup_file_path() -> Path:
    return get_startup_dir() / STARTUP_NAME

def is_startup_enabled() -> bool:
    return get_startup_file_path().exists()

def enable_startup(target_script_path: str = None) -> bool:
    """Creates a Windows shortcut in the Startup folder."""
    try:
        startup_path = get_startup_file_path()
        if not target_script_path:
            if getattr(sys, "frozen", False):
                runner = str(Path(sys.executable).resolve())
                arguments_arg = ""
                working_dir = str(Path(sys.executable).resolve().parent)
            else:
                base_dir = Path(__file__).resolve().parent.parent
                target_script_path = str(base_dir / "main.pyw")
                python_exe = Path(sys.executable)
                pythonw_exe = python_exe.parent / "pythonw.exe"
                runner = str(pythonw_exe) if pythonw_exe.exists() else str(python_exe)
                arguments_arg = f'$Shortcut.Arguments = \'"{target_script_path}"\''
                working_dir = str(Path(target_script_path).parent)
        else:
            python_exe = Path(sys.executable)
            pythonw_exe = python_exe.parent / "pythonw.exe"
            runner = str(pythonw_exe) if pythonw_exe.exists() else str(python_exe)
            arguments_arg = f'$Shortcut.Arguments = \'"{target_script_path}"\''
            working_dir = str(Path(target_script_path).parent)

        ps_script = f"""
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut('{str(startup_path)}')
$Shortcut.TargetPath = '{runner}'
{arguments_arg}
$Shortcut.WorkingDirectory = '{working_dir}'
$Shortcut.Description = 'GravPulse AI Quota Monitor'
$Shortcut.Save()
"""
        create_no_window = getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000)
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_script],
            check=True,
            capture_output=True,
            timeout=5,
            creationflags=create_no_window
        )
        return startup_path.exists()
    except Exception:
        return False

def disable_startup() -> bool:
    """Removes shortcut from Startup folder."""
    try:
        path = get_startup_file_path()
        if path.exists():
            path.unlink()
        return not path.exists()
    except Exception:
        return False

def toggle_startup() -> bool:
    if is_startup_enabled():
        disable_startup()
        return False
    else:
        enable_startup()
        return True
