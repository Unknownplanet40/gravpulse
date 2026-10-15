import os
import sys
import html
import winreg
import subprocess
from pathlib import Path

APP_ID = "GravPulse"
PROJECT_DIR = Path(__file__).resolve().parent.parent
ICON_ICO = PROJECT_DIR / "assets" / "ico" / "app.ico"
ICON_PNG = PROJECT_DIR / "assets" / "png" / "app-icon-48.png"

def ensure_app_registered():
    """Registers GravPulse in Windows AppUserModelId and Start Menu for branded toast notifications."""
    try:
        # 1. Register in HKCU\Software\Classes\AppUserModelId\GravPulse
        reg_path = rf"Software\Classes\AppUserModelId\{APP_ID}"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, "GravPulse")
            winreg.SetValueEx(key, "IconUri", 0, winreg.REG_SZ, str(ICON_PNG))
            winreg.SetValueEx(key, "ShowInSettings", 0, winreg.REG_DWORD, 1)

        # 2. Ensure Start Menu shortcut exists with AppId
        appdata = os.environ.get("APPDATA", "")
        if appdata:
            programs_dir = Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
            shortcut_path = programs_dir / f"{APP_ID}.lnk"
            if not shortcut_path.exists():
                vbs_code = f"""
                Set wsh = CreateObject("WScript.Shell")
                Set sc = wsh.CreateShortcut("{shortcut_path}")
                sc.TargetPath = "{PROJECT_DIR / 'run.vbs'}"
                sc.IconLocation = "{ICON_ICO}"
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
