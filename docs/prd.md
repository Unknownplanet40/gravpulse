# Product Requirements Document: Antigravity Quota Widget

## Product Overview

**Product Vision:** A lightweight, persistent Windows System Tray widget that monitors and displays Antigravity AI rate limits and refresh countdowns directly on the desktop.

**Target Users:** Developers using Google Antigravity who need immediate visibility into their 5-hour and weekly quota without navigating inside the IDE.

**Business & Technical Objectives:**
- Zero cloud API configuration required: automatically discovers local Antigravity Language Server RPC.
- Instant, non-intrusive awareness via dynamic system tray icon badges and desktop popup cards.
- Background polling with proactive desktop toast alerts for low quota and refreshed quotas.

---

## User Personas

### Persona: AI Developer / Power User
- **Demographics:** Software engineer pair-programming extensively with Antigravity AI models.
- **Goals:** Track model usage (Gemini & Claude/GPT models) to pace coding sessions effectively.
- **Pain Points:** Finding out unexpectedly that the weekly quota is exhausted mid-session.
- **User Journey:** Glances at the Windows taskbar icon color (Green/Yellow/Red); clicks for exact countdown timers and percentages; receives toast alerts when quotas refresh.

---

## Feature Requirements

| Feature | Description | Priority | Acceptance Criteria |
|---------|-------------|----------|---------------------|
| **Auto-Discovery** | Detects running `language_server.exe` PID, CSRF token, and RPC port | Must | Connects without manual token entry |
| **Dynamic Tray Icon** | 64x64 icon with color status dot (Green >50%, Amber 15-50%, Red <15%) | Must | Updates icon on every poll cycle |
| **Dark Theme Popup** | Floating card with circular progress rings and reset countdowns | Must | Matches Antigravity IDE styling; dismisses on click-away |
| **Background Polling** | 60-second periodic fetch with change detection | Must | Low CPU/memory footprint; sub-50ms query |
| **Windows Toast Alerts** | Native notification when limit drops <10% or resets | Should | Uses Windows Shell notification |
| **Start with Windows** | Toggle startup shortcut in `shell:startup` | Should | Creates/removes shortcut with 1-click |

---

## User Flows

### Flow 1: Daily Usage & Inspection
1. User boots Windows or runs `run.bat` / `pythonw main.pyw`.
2. Widget appears in Windows System Tray with status badge.
3. User single-clicks tray icon to toggle popup card.
4. User inspects circular progress rings, percentages, and countdowns ("Refreshes in 1 day, 13 hours").
5. User clicks anywhere outside the card to dismiss.

### Flow 2: Quota Warnings & Refresh Alerts
1. Background worker polls local endpoint every 60 seconds.
2. If remaining quota falls below 10%, a Windows toast notification fires.
3. When the countdown expires and quota resets, a notification confirms the refresh.