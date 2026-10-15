# GravPulse

> **Track your Antigravity AI quotas in real time.**

GravPulse is a zero-config Windows 11 system tray widget that hooks directly into your local Antigravity language server RPC to monitor AI model quotas. Track 5-hour and weekly quotas for Gemini, Claude, and GPT models with live reset countdowns and native desktop alerts—no cloud API keys required.

---

## Highlights

- **Zero-Config Auto-Discovery:** Seamlessly connects to your locally running Antigravity Language Server RPC (`language_server.exe`) via internal ConnectRPC protocol. Zero cloud API tokens or authentication keys needed.
- **Windows 11 Fluent Design:** Borderless, 100% solid dark-mode popover card with hardware-level GDI rounded corners (16px), native DWM drop shadow, Segoe UI typography, and subtle interactive hover states.
- **Smart Best-Available Status:** System tray icon reflects your active coding capacity. If Gemini is full (92%) and Claude is exhausted (0%), your tray icon stays **Green (Active)** so you know you can keep coding without interruption.
- **Cached Offline Mode with Clock Math:** If Antigravity closes, GravPulse retains your last known quota and continuously recalculates reset countdowns live against your system clock—with an amber indicator dot and a 1-click **Open Antigravity** launcher.
- **Proactive Notifications:** Automatic Windows toast alerts when a model limit drops below 10% or fully resets.
- **System Theme Adaptation:** Automatically syncs with Windows Dark Mode or Light Mode preferences, with manual overrides via right-click context menu.

---

## Quickstart

### Prerequisites
- Windows 10/11
- Python 3.10+ (with `tkinter`)
- Google Antigravity IDE

### 1. Installation
Clone the repository and install the lightweight dependencies:
```powershell
git clone https://github.com/<your-username>/gravpulse.git
cd gravpulse
pip install -r requirements.txt
```

### 2. Launch
Start GravPulse silently in the background:
- Double-click `run.vbs` (or `run.bat`), or run via PowerShell:
  ```powershell
  pythonw main.pyw
  ```

---

## Usage


 Action | Description |
 :--- | :--- |
| **Left-Click Tray Icon** | Toggles the fluent popover card showing circular progress rings, remaining percentages, and exact reset dates/times. |
| **Right-Click Tray Icon** | Displays quick connectivity status (`Status: Online`), manual **Refresh Now**, **Theme** picker (System, Dark, Light), **Start with Windows** toggle, and **Exit**. |
| **Hover Limit Rows** | Displays flyout tooltips explaining quota rules and exact reset datetimes in your local timezone. |
| **Offline State** | Shows an amber status dot with a 1-click Windows 11 Fluent **Open Antigravity** launch button. |

---

## Tray Status Indicator

GravPulse uses an intelligent best-available capacity algorithm so you always know your true coding status:

| Icon Status | Condition | Meaning |
| :--- | :--- | :--- |
| <img src="docs\gravpulse-assets\svg\tray-active.svg" width="32"/>  |  Best model capacity > 50% | High capacity available. Ready for heavy pair programming. |
| <img src="docs\gravpulse-assets\svg\tray-warning.svg" width="32"/>  | Best model capacity 1% – 50% | Capacity is half-depleted or nearing reset window. Pace your requests. |
| <img src="docs\gravpulse-assets\svg\tray-exhausted.svg" width="32"/>  | 0% across ALL model groups | All models exhausted. Waiting on countdown reset. |
| <img src="docs\gravpulse-assets\svg\tray-offline.svg" width="32"/>  | Disconnected / No Cache | Antigravity is closed and no prior quota snapshot exists. |

---

## Repository Structure

```
├── assets/                 # GravPulse official visual brand assets
│   ├── ico/app.ico         # Application icon
│   ├── png/                # High-res logos and app marks (16px to 1024px)
│   ├── svg/                # Scalable vector sources
│   └── tray/               # Multi-resolution tray status PNGs (active, warning, exhausted, offline)
├── src/
│   ├── collector.py        # Antigravity ConnectRPC auto-discovery & cached offline countdown engine
│   ├── popup.py            # Windows 11 Fluent Tkinter popover window with circular progress rings
│   ├── tray.py             # Pystray tray daemon with smart status evaluation & themed Win32 context menu
│   ├── theme.py            # Windows registry dark/light mode detection & color palettes
│   └── startup.py          # Windows shell:startup shortcut manager
├── tests/
│   └── test_collector.py   # Automated unit test suite (10/10 passing)
├── docs/                   # Product requirements (PRD), architecture, and asset guides
├── main.pyw                # Single-instance application coordinator & background poller
├── run.vbs                 # Windowless background launcher (zero console flash)
├── run.bat                 # 1-click batch launcher
├── requirements.txt        # Minimal dependencies (psutil, pystray, Pillow)
├── PROJECT-LOG.md          # Permanent append-only session history & decision log
└── handoff.md              # Active state and next steps snapshot
```

---

## Running Tests

GravPulse includes an automated test suite verifying process discovery, countdown calculation, tray icon generation, and theme resolution:

```powershell
python -m unittest tests/test_collector.py
```

---

## License

MIT License. Designed with care for developers using Google Antigravity.
