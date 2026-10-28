# Handoff

## 1. Goal
Provide a standalone, branded Windows desktop system tray widget monitoring Antigravity AI quotas and models in real time, with single branded notifications, standalone `.exe` distribution, and automatic release asset deployment on GitHub.

## 2. Current State
- **Branch**: `main`
- **Commit Hash Pushed**: `6c8048a`
- **Push Status**: Pushed and synchronized with `origin/main` (`a4cb1a2..6c8048a`).
- **Automated CI Release**: Triggered on GitHub Actions (workflow run `Release` in progress for auto-version bump to `v0.3.0`).
- **Binary Status**: Local `dist/GravPulse.exe` verified with full PE version resource details (`0.2.0.0` / `GravPulse`).
- **Unit Tests**: 18/18 passing (`tests/test_collector.py`, `tests/test_skills.py`, `tests/test_paths.py`).

## 3. Active Files
- `GravPulse.spec` (PyInstaller packaging specification with dynamic `VERSION` sync)
- `version_info.txt` (Windows PE `VSVersionInfo` definition for FileDescription, ProductVersion, Copyrights)
- `build.bat` (1-click local Windows build script)
- `src/paths.py` (Centralized resource path resolution for dev and frozen `sys._MEIPASS`)
- `.github/workflows/release.yml` (`build-windows-exe` job uploading `GravPulse.exe` to GitHub Releases)
- `src/notification.py` (Branded Windows toast with LocalAppData icon caching)
- `main.pyw` (Entry point, single notification call, single instance handling)
- `src/startup.py` (Creates shortcut targeting `sys.executable` when running as frozen binary)
- `PROJECT-LOG.md` (Permanent append-only historical record)

## 4. Changes Made
- Eliminated double notification bug by removing duplicate `self.tray.icon.notify` calls in `main.pyw` and `src/tray.py`.
- Implemented `src/paths.py` to transparently resolve asset paths across dev mode and PyInstaller frozen temp directory (`sys._MEIPASS`).
- Created `GravPulse.spec` embedding `assets/`, tray icons, app icon, and auto-syncing Windows version information.
- Added PE metadata (`CompanyName`, `FileDescription`, `FileVersion`, `ProductName`, `ProductVersion`, `LegalCopyright`, `Comments`).
- Created `build.bat` script for 1-click local compilation into `dist/GravPulse.exe`.
- Added `build-windows-exe` job to `.github/workflows/release.yml` on `windows-latest` to build and upload `GravPulse.exe` directly to GitHub Releases.
- Added `tests/test_paths.py` verifying path resolution and frozen simulation.
- Committed `6c8048a` and pushed to `main`.

## 5. Failed Attempts
- Direct overwrite of `dist/GravPulse.exe` failed initially with `PermissionError: [WinError 5]` because a test instance was still running; resolved by stopping existing test process before rebuilding.

## 6. Specific Next Steps
1. Verify GitHub Actions completes release `v0.3.0` and uploads `GravPulse.exe` to the release assets.
2. Download and verify the release executable on a clean Windows machine without Python installed.
