# Changelog

All notable changes to this project are documented here.

## [Unreleased]

## [0.2.0] - 2026-10-15

### Added
- Plan tier and account email detection via ConnectRPC `GetUserStatus` and `GetUnleashData` in `src/collector.py`. (8bbf1ed)
- Dynamic plan tier badge and active email subtitle in `src/popup.py`. (8bbf1ed)
- Account switch persistence footnote with interactive hover tooltip in `src/popup.py`. (8bbf1ed)
- Fast asynchronous refresh hook upon clicking tray icon or toggling popup in `src/tray.py`. (8bbf1ed)
- Unit tests for plan tier formatting, account switch cache invalidation, and offline cache TTL in `tests/test_collector.py`. (8bbf1ed)
- Tracked `assets/banner.jpg` project banner preview. (5d9de63)

### Changed
- Sorted detected `language_server.exe` processes by `create_time` descending in `src/collector.py` so newest process is always selected over lingering processes. (8bbf1ed)
- Purge cached quota immediately when PID or account email changes in `src/collector.py`. (8bbf1ed)
- Reduced background polling interval from 60s to 15s in `main.pyw`. (8bbf1ed)
- Reset alert thresholds when switching accounts in `main.pyw` to prevent spurious refresh alerts. (8bbf1ed)
- point version.json at release v0.1.0 [skip ci] (653ee1f)

### Fixed
- Prevented previous account's quota from displaying when switching accounts in Antigravity. (8bbf1ed)
- Added 5-minute TTL to offline fallback cache to avoid showing stale data indefinitely. (8bbf1ed)
- Replaced broken `docs\gravpulse-assets\svg\...` paths in `README.md` with valid web relative paths `assets/svg/tray-*.svg`. (5d9de63)


## [0.1.0] - 2026-10-15

### Added
- Internal ConnectRPC auto-discovery and rate limit polling engine (`src/collector.py`). (61200be)
- Windows 11 Fluent popup card with circular SVG/Tk progress rings, hover tooltips, and 16px GDI rounded corners (`src/popup.py`). (61200be)
- Pystray system tray daemon with smart best-available status logic and context menu icons (`src/tray.py`). (61200be)
- Windows Runtime native Toast notification dispatcher with audio chime and circular app mark (`src/notification.py`). (61200be)
- Automatic Windows dark and light theme adaptation via registry poller (`src/theme.py`). (61200be)
- Windows Startup shortcut management (`src/startup.py`). (61200be)
- Single-instance IPC socket coordination and windowless VBScript launcher (`run.vbs`, `main.pyw`). (61200be)
- Official GravPulse visual assets in ICO, PNG, SVG, and multi-resolution tray formats (`assets/`). (61200be)
- Automated unit test suite with 11 passing tests (`tests/test_collector.py`). (61200be)
- Complete documentation: PRD, architecture, update guide, and clean README (`docs/`, `README.md`). (61200be)

### Changed
- README completely updated with GravPulse brand identity, tagline, elevator pitch, and status matrix. (61200be)

### Security
- Hardened `.gitignore` to block environment secrets, private keys, certificates, credentials, logs, crash dumps, and Windows shortcuts. (61200be)

