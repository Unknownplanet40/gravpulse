import pystray
from PIL import Image, ImageDraw
from src.startup import is_startup_enabled, toggle_startup
from src.theme import get_theme, get_rgb_status_color, apply_win32_theme

import os
from pathlib import Path

_ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets" / "tray"

def create_tray_icon(percent=100.0, is_online=True, theme_pref="system", size=64):
    """Loads official GravPulse tray asset based on status (active, warning, exhausted, offline)."""
    # 1. Determine status:
    # - active (green): best model > 50%
    # - warning (yellow): best model 1% - 50%
    # - exhausted (red): 0% across ALL models
    # - offline: not connected and no cache
    if not is_online or percent is None:
        status = "offline"
    elif percent <= 0.0:
        status = "exhausted"
    elif percent <= 50.0:
        status = "warning"
    else:
        status = "active"

    # 2. Try loading official pre-rendered multi-resolution PNG
    icon_path = _ASSETS_DIR / f"{status}-{size if size in (16,20,24,32,48,64,256) else 64}.png"
    if icon_path.exists():
        try:
            return Image.open(icon_path).convert("RGBA")
        except Exception:
            pass

    # 3. Fallback procedural render
    img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    theme = get_theme(theme_pref)

    draw.ellipse((4, 4, 60, 60), fill=theme["icon_bg"], outline=theme["icon_border"], width=2)
    cx, cy = 32, 32
    star_points = [
        (cx, cy - 18), (cx + 4, cy - 5), (cx + 18, cy), (cx + 4, cy + 5),
        (cx, cy + 18), (cx - 4, cy + 5), (cx - 18, cy), (cx - 4, cy - 5),
    ]
    star_color = theme["icon_star"] if is_online else (120, 125, 135, 200)
    draw.polygon(star_points, fill=star_color)

    dot_color = get_rgb_status_color(percent if is_online else None)
    draw.ellipse((42, 42, 60, 60), fill=dot_color, outline=theme["icon_border"][:3], width=2)
    return img

class AntigravityTrayApp:
    """Manages the Windows System Tray Icon, menu, and popup window integration."""
    def __init__(self, collector, popup_window, on_exit=None, theme_preference="system"):
        self.collector = collector
        self.popup = popup_window
        self.on_exit = on_exit
        self.theme_preference = theme_preference
        self.current_quota = None

        # Apply system / dark / light Win32 theme preference
        apply_win32_theme(self.theme_preference)

        initial_img = create_tray_icon(100.0, is_online=False, theme_pref=self.theme_preference)
        self.icon = pystray.Icon(
            "GravPulse",
            initial_img,
            "GravPulse",
            menu=self._build_menu()
        )

        # Hook right-click to ensure Win32 context menu inherits active theme
        try:
            import pystray._util.win32 as win32
            if hasattr(self.icon, '_message_handlers') and win32.WM_NOTIFY in self.icon._message_handlers:
                orig_notify = self.icon._message_handlers[win32.WM_NOTIFY]
                def _themed_notify(wparam, lparam):
                    if lparam == 0x0205:  # WM_RBUTTONUP
                        hwnds = [getattr(self.icon, '_hwnd', None), getattr(self.icon, '_menu_hwnd', None)]
                        apply_win32_theme(self.theme_preference, hwnds=hwnds)
                    return orig_notify(wparam, lparam)
                self.icon._message_handlers[win32.WM_NOTIFY] = _themed_notify
        except Exception:
            pass

    def set_theme(self, pref):
        self.theme_preference = pref
        hwnds = [getattr(self.icon, '_hwnd', None), getattr(self.icon, '_menu_hwnd', None)] if self.icon else []
        apply_win32_theme(self.theme_preference, hwnds=hwnds)
        if self.popup:
            self.popup.set_theme_preference(pref)
        if self.current_quota:
            self.update_quota(self.current_quota)
        elif self.icon:
            self.icon.icon = create_tray_icon(100.0, is_online=False, theme_pref=self.theme_preference)
            self.icon.menu = self._build_menu()

    def _trigger_fast_refresh(self):
        """Asynchronously triggers a fast refresh so account/quota changes appear immediately."""
        import threading
        def _worker():
            try:
                data = self.collector.get_quota(force_refresh=True)
                self.update_quota(data)
                if self.popup and self.popup.is_visible:
                    if self.popup.parent:
                        self.popup.parent.after(0, lambda: self.popup.update_data(data))
                    else:
                        self.popup.update_data(data)
            except Exception:
                pass
        threading.Thread(target=_worker, daemon=True).start()

    def _show_popup(self):
        if self.popup:
            if self.popup.parent:
                self.popup.parent.after(0, lambda: self.popup.show(self.current_quota))
            else:
                self.popup.show(self.current_quota)
        self._trigger_fast_refresh()

    def _toggle_popup(self):
        if self.popup:
            if self.popup.parent:
                self.popup.parent.after(0, lambda: self.popup.toggle(self.current_quota))
            else:
                self.popup.toggle(self.current_quota)
        self._trigger_fast_refresh()

    def _on_left_click(self, icon, item):
        self._toggle_popup()

    def _on_refresh_clicked(self, icon, item):
        data = self.collector.get_quota(force_refresh=True)
        self.update_quota(data)
        if self.popup:
            if self.popup.parent:
                self.popup.parent.after(0, lambda: self.popup.update_data(data))
            else:
                self.popup.update_data(data)

    def _on_test_notification(self, icon, item):
        from src.notification import send_windows_toast
        try:
            if self.icon:
                self.icon.notify("Claude 3.5 Sonnet (5h) has refreshed to 100%!", "GravPulse: Quota Refreshed")
        except Exception:
            pass
        send_windows_toast("GravPulse: Quota Refreshed", "Claude 3.5 Sonnet (5h) has refreshed to 100%!")

    def _on_toggle_startup(self, icon, item):
        toggle_startup()

    def _on_exit_clicked(self, icon, item):
        if self.popup:
            if self.popup.parent:
                self.popup.parent.after(0, self.popup.hide)
            else:
                self.popup.hide()
        if self.icon:
            self.icon.stop()
        if self.on_exit:
            self.on_exit()

    def _build_menu(self):
        menu_items = []

        # Top item: Status indicator (Online, Offline, or Offline (Cached))
        is_online = bool(self.current_quota and self.current_quota.get("online"))
        is_cached = bool(self.current_quota and self.current_quota.get("cached"))
        has_groups = bool(self.current_quota and self.current_quota.get("groups"))

        if is_online:
            status_text = "Status: Online"
        elif is_cached or has_groups:
            status_text = "Status: Offline (Cached)"
        else:
            status_text = "Status: Offline"

        menu_items.append(pystray.MenuItem(status_text, lambda: None, enabled=False))
        menu_items.append(pystray.MenuItem("View Details", lambda icon, item: self._show_popup(), default=True))
        menu_items.append(pystray.MenuItem("Refresh Now", self._on_refresh_clicked))
        """ menu_items.append(pystray.MenuItem("Test Notification", self._on_test_notification)) """

        # Theme submenu
        theme_menu = pystray.Menu(
            pystray.MenuItem(
                "System Default",
                lambda icon, item: self.set_theme("system"),
                checked=lambda item: self.theme_preference == "system"
            ),
            pystray.MenuItem(
                "Dark Mode",
                lambda icon, item: self.set_theme("dark"),
                checked=lambda item: self.theme_preference == "dark"
            ),
            pystray.MenuItem(
                "Light Mode",
                lambda icon, item: self.set_theme("light"),
                checked=lambda item: self.theme_preference == "light"
            )
        )
        menu_items.append(pystray.MenuItem("Theme", theme_menu))

        menu_items.append(pystray.MenuItem(
            "Start with Windows",
            self._on_toggle_startup,
            checked=lambda item: is_startup_enabled()
        ))
        menu_items.append(pystray.Menu.SEPARATOR)
        menu_items.append(pystray.MenuItem("Exit", self._on_exit_clicked))

        return pystray.Menu(*menu_items)

    def update_quota(self, quota_data):
        self.current_quota = quota_data
        if not self.icon:
            return

        is_online = quota_data.get("online", False)
        is_cached = quota_data.get("cached", False)
        groups = quota_data.get("groups", [])

        # Smart Best-Available Model capacity calculation:
        # Each model group's capacity is constrained by its lowest bucket (e.g. 5h vs weekly).
        # The user's coding ability is determined by the BEST available model group.
        # - If Gemini has 92% and Claude has 0%, best model is 92% -> Icon is GREEN.
        # - If best model is between 1% and 50%, icon is YELLOW.
        # - If ALL models are 0% depleted, best model is 0% -> Icon is RED (exhausted).
        if is_online or (is_cached and groups):
            group_capacities = []
            for g in groups:
                b_pcts = [float(b.get("percent", 100.0)) for b in g.get("buckets", [])]
                if b_pcts:
                    group_capacities.append(min(b_pcts))
            best_model_pct = max(group_capacities) if group_capacities else 100.0
            display_online = True
        else:
            best_model_pct = None
            display_online = False

        # Update tray icon image
        self.icon.icon = create_tray_icon(
            best_model_pct,
            is_online=display_online,
            theme_pref=self.theme_preference
        )

        # Update tooltip (Win32 limit is strictly 128 chars)
        if is_online:
            tooltip_lines = ["GravPulse:"]
            for g in quota_data.get("groups", []):
                short_group = "Gemini" if "gemini" in g.get("name", "").lower() else "Claude"
                parts = []
                for b in g.get("buckets", []):
                    short_window = "Wk" if "week" in b.get("name", "").lower() else "5h"
                    parts.append(f"{short_window}:{int(b.get('percent', 0))}%")
                if parts:
                    tooltip_lines.append(f"{short_group} " + " ".join(parts))
            full_tooltip = "\n".join(tooltip_lines)
            self.icon.title = full_tooltip[:120]
        else:
            self.icon.title = "GravPulse: Offline"

        # Update context menu
        self.icon.menu = self._build_menu()

    def run(self, on_ready=None):
        """Runs the tray icon event loop."""
        def _setup(icon):
            icon.visible = True
            hwnds = [getattr(icon, '_hwnd', None), getattr(icon, '_menu_hwnd', None)]
            apply_win32_theme(self.theme_preference, hwnds=hwnds)
            if on_ready:
                on_ready(icon)

        self.icon.run(setup=_setup)
