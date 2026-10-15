# Changelog

All notable changes to this project are documented here.

## [Unreleased]

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

