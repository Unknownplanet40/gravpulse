import os
import sys
from pathlib import Path

def get_base_dir() -> Path:
    """Returns application root directory whether running as script or frozen PyInstaller exe."""
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", sys.executable if os.path.isdir(sys.executable) else Path(sys.executable).parent))
    return Path(__file__).resolve().parent.parent

def get_resource_path(relative_path: str) -> Path:
    """Resolves relative resource path (e.g. assets/...) to an absolute Path."""
    return get_base_dir() / relative_path

def get_app_dir() -> Path:
    """Returns directory where executable or main.pyw lives (for persistent user data/logs)."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent
