"""Drop-in tray icon loader for pystray. Assets live in ./tray/."""
from __future__ import annotations
from pathlib import Path
from typing import Literal
from PIL import Image

Status = Literal["active", "warning", "exhausted", "offline"]
_ASSETS = Path(__file__).parent / "tray"
_VALID: frozenset[str] = frozenset({"active", "warning", "exhausted", "offline"})


def tray_icon(status: Status, size: int = 64) -> Image.Image:
    """Return the tray image for a status. Raises ValueError on bad input."""
    if status not in _VALID:
        raise ValueError(f"Unknown status: {status!r}")
    path = _ASSETS / f"{status}-{size if size in (16,20,24,32,48,64,256) else 64}.png"
    return Image.open(path).convert("RGBA")


def status_for(percent_left: float | None) -> Status:
    """Map remaining quota (0-100) to a status. None = can't reach server."""
    if percent_left is None:
        return "offline"
    if percent_left <= 0:
        return "exhausted"
    if percent_left <= 20:
        return "warning"
    return "active"

# Usage with pystray:
#   icon = pystray.Icon("GravPulse", tray_icon("active"), "GravPulse")
#   icon.icon = tray_icon(status_for(pct))   # swap on each poll
