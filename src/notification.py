import os
import sys
import html
import winreg
import subprocess
import shutil
from pathlib import Path
from src.paths import get_resource_path, get_base_dir

APP_ID = "GravPulse"
ICON_ICO = get_resource_path("assets/ico/app.ico")
ICON_PNG = get_resource_path("assets/png/app-icon-48.png")

def ensure_app_registered():
    """Registers GravPulse in Windows AppUserModelId and Start Menu for branded toast notifications."""
    try:
        # Cache permanent icon copy in local appdata for reliable Windows notification display
        appdata_local = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "GravPulse"
        appdata_local.mkdir(parents=True, exist_ok=True)
        permanent_png = appdata_local / "app-icon-48.png"
        permanent_ico = appdata_local / "app.ico"
        if not permanent_png.exists() and ICON_PNG.exists():
            shutil.copy2(ICON_PNG, permanent_png)
        if not permanent_ico.exists() and ICON_ICO.exists():
            shutil.copy2(ICON_ICO, permanent_ico)

        icon_for_reg = str(permanent_png if permanent_png.exists() else ICON_PNG)
        icon_for_sc = str(permanent_ico if permanent_ico.exists() else ICON_ICO)

        # 1. Register in HKCU\Software\Classes\AppUserModelId\GravPulse
        reg_path = rf"Software\Classes\AppUserModelId\{APP_ID}"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, "GravPulse")
            winreg.SetValueEx(key, "IconUri", 0, winreg.REG_SZ, icon_for_reg)
            winreg.SetValueEx(key, "ShowInSettings", 0, winreg.REG_DWORD, 1)

        # 2. Ensure Start Menu shortcut exists with AppId
        appdata = os.environ.get("APPDATA", "")
        if appdata:
            programs_dir = Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
            shortcut_path = programs_dir / f"{APP_ID}.lnk"
            if not shortcut_path.exists():
                if getattr(sys, "frozen", False):
                    target_exec = str(Path(sys.executable).resolve())
                else:
                    target_exec = str((get_base_dir() / "run.vbs").resolve())

                vbs_code = f"""
                Set wsh = CreateObject("WScript.Shell")
                Set sc = wsh.CreateShortcut("{shortcut_path}")
                sc.TargetPath = "{target_exec}"
                sc.IconLocation = "{icon_for_sc}"
                sc.Description = "Track Antigravity AI quotas in real time."
                sc.Save
                """
                subprocess.run(["cscript", "//nologo", "//e:vbscript"], input=vbs_code, text=True, capture_output=True)
    except Exception:
        pass

def send_windows_toast(title: str, message: str, icon_override: str = None):
    """Sends a native Windows 10/11 toast notification with GravPulse logo, sound, and clean branding."""
    ensure_app_registered()

    clean_title = html.escape(title)
    clean_msg = html.escape(message)
    icon_file = icon_override or str(ICON_PNG)

    # Toast XML with circular GravPulse app logo beside the content text
    xml_content = (
        f'<toast>'
        f'<visual>'
        f'<binding template="ToastGeneric">'
        f'<image placement="appLogoOverride" hint-crop="circle" src="{icon_file}" />'
        f'<text>{clean_title}</text>'
        f'<text>{clean_msg}</text>'
        f'</binding>'
        f'</visual>'
        f'<audio src="ms-winsoundevent:Notification.Default" />'
        f'</toast>'
    )

    ps_script = f"""
    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
    [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
    $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
    $xml.LoadXml(@'
{xml_content}
'@)
    $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
    try {{
        [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("{APP_ID}").Show($toast)
    }} catch {{
        [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("{{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}}\\WindowsPowerShell\\v1.0\\powershell.exe").Show($toast)
    }}
    """

    try:
        CREATE_NO_WINDOW = 0x08000000
        subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-Command", "-"],
            input=ps_script,
            text=True,
            capture_output=True,
            timeout=5,
            creationflags=CREATE_NO_WINDOW
        )
    except Exception:
        pass

if __name__ == "__main__":
    t = sys.argv[1] if len(sys.argv) > 1 else "GravPulse: Quota Refreshed"
    m = sys.argv[2] if len(sys.argv) > 2 else "Claude 3.5 Sonnet (5h) has refreshed to 100%!"
    send_windows_toast(t, m)
