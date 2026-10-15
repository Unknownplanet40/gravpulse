import os
import subprocess
import tkinter as tk
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageTk
from src.theme import get_theme, get_status_color, COLOR_RED

_APP_ICON_PATH = Path(__file__).resolve().parent.parent / "assets" / "png" / "app-icon-32.png"

def launch_antigravity():
    """Launches Antigravity application in detached background process."""
    paths = [
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Antigravity\Antigravity.exe"),
        os.path.expandvars(r"%PROGRAMFILES%\Antigravity\Antigravity.exe")
    ]
    for exe in paths:
        if os.path.exists(exe):
            try:
                detached = 0x00000008  # DETACHED_PROCESS
                create_no_window = getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000)
                subprocess.Popen([exe], creationflags=detached | create_no_window, close_fds=True)
                return True
            except Exception:
                pass
    return False

def format_reset_datetime(reset_iso_str):
    """Formats ISO reset timestamp into '%A, %B %d, %Y, at %I:%M %p' in local timezone."""
    if not reset_iso_str:
        return ""
    try:
        clean_str = reset_iso_str.replace("Z", "+00:00")
        dt_utc = datetime.fromisoformat(clean_str)
        dt_local = dt_utc.astimezone()
        return dt_local.strftime("%A, %B %d, %Y, at %I:%M %p")
    except Exception:
        return ""

class HoverTooltip:
    """Displays a clean floating description tooltip when hovering over an item row."""
    def __init__(self, widgets, text, theme=None):
        self.widgets = widgets if isinstance(widgets, list) else [widgets]
        self.text = text
        self.theme = theme
        self.tip_window = None
        for w in self.widgets:
            w.bind("<Enter>", self.show_tip, add="+")
            w.bind("<Leave>", self.hide_tip, add="+")
            w.bind("<Button-1>", self.hide_tip, add="+")

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        w = self.widgets[0]
        try:
            bg_col = self.theme.get("tooltip_bg", "#1c1d22") if self.theme else "#1c1d22"
            border_col = self.theme.get("tooltip_border", "#525666") if self.theme else "#525666"
            fg_col = self.theme.get("text_primary", "#ffffff") if self.theme else "#ffffff"

            self.tip_window = tw = tk.Toplevel(w)
            tw.withdraw()
            tw.wm_overrideredirect(True)
            tw.wm_attributes("-topmost", True)

            frame = tk.Frame(
                tw,
                bg=bg_col,
                highlightthickness=1,
                highlightbackground=border_col
            )
            frame.pack(fill=tk.BOTH, expand=True)

            lbl = tk.Label(
                frame,
                text=self.text,
                justify=tk.LEFT,
                bg=bg_col,
                fg=fg_col,
                font=("Segoe UI", 8),
                wraplength=260,
                padx=10,
                pady=6
            )
            lbl.pack()

            tw.update_idletasks()
            tip_w = tw.winfo_reqwidth()
            tip_h = tw.winfo_reqheight()

            # Determine item root coordinates safely
            rx = w.winfo_rootx()
            ry = w.winfo_rooty()
            if (rx <= 1 or ry <= 1) and event:
                rx = getattr(event, "x_root", 1200) - 20
                ry = getattr(event, "y_root", 600)

            screen_w = tw.winfo_screenwidth()
            screen_h = tw.winfo_screenheight()

            # Position to the left of the item row
            x = rx - tip_w - 12
            y = ry - 2

            # Keep inside visible screen bounds
            if x < 10:
                x = rx + w.winfo_width() + 12
            if y + tip_h > screen_h - 40:
                y = screen_h - tip_h - 40
            if y < 10:
                y = 10

            tw.wm_geometry(f"{tip_w}x{tip_h}+{x}+{y}")
            tw.deiconify()
        except Exception:
            pass

    def hide_tip(self, event=None):
        if self.tip_window:
            try:
                self.tip_window.destroy()
            except Exception:
                pass
            self.tip_window = None

class QuotaPopupWindow:
    """Floating popover card matching Antigravity native UI with hover descriptions."""
    def __init__(self, parent_root=None, on_refresh_callback=None, theme_preference="system"):
        self.parent = parent_root
        self.window = None
        self.on_refresh_callback = on_refresh_callback
        self.theme_preference = theme_preference
        self.is_visible = False
        self.cached_quota = None
        self.tooltips = []

    def set_theme_preference(self, pref):
        self.theme_preference = pref
        if self.is_visible and self.window is not None and self.window.winfo_exists():
            self._render()

    def show(self, quota_data=None):
        if quota_data:
            self.cached_quota = quota_data

        theme = get_theme(self.theme_preference)

        if self.window is not None and self.window.winfo_exists():
            if self.is_visible:
                self.hide()
                return
            else:
                self._render()
                self._position_window()
                self.window.deiconify()
                self.window.lift()
                self.window.focus_force()
                self.is_visible = True
                return

        # Create Toplevel or Tk window
        if self.parent and self.parent.winfo_exists():
            self.window = tk.Toplevel(self.parent)
        else:
            self.window = tk.Tk()

        self.window.withdraw()
        self.window.title("GravPulse")
        self.window.overrideredirect(True)
        self.window.configure(bg=theme["bg"])
        self.window.attributes("-topmost", True)

        # Close on clicking outside or escape
        self.window.bind("<FocusOut>", lambda e: self.hide())
        self.window.bind("<Escape>", lambda e: self.hide())

        self._render()
        self._position_window()
        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()
        self.is_visible = True

    def hide(self):
        # Clean up any active tooltip windows
        for tip in self.tooltips:
            tip.hide_tip()
        if self.window is not None and self.window.winfo_exists():
            self.window.withdraw()
            self.is_visible = False

    def toggle(self, quota_data=None):
        if self.is_visible:
            self.hide()
        else:
            self.show(quota_data)

    def update_data(self, quota_data):
        self.cached_quota = quota_data
        if self.is_visible and self.window is not None and self.window.winfo_exists():
            self._render()

    def _trigger_refresh(self):
        if self.on_refresh_callback:
            data = self.on_refresh_callback()
            if data:
                self.update_data(data)

    def _apply_native_styling(self, w=304, h=300):
        """Applies Windows 11 DWM rounded corners and GDI region clipping using exact dimensions."""
        try:
            import ctypes
            top_hwnd = ctypes.windll.user32.GetParent(self.window.winfo_id()) or self.window.winfo_id()

            # 1. Native Windows 11 DWM Corner Preference: DWMWCP_ROUND (2)
            DWMWA_WINDOW_CORNER_PREFERENCE = 33
            DWMWCP_ROUND = ctypes.c_int(2)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                top_hwnd,
                DWMWA_WINDOW_CORNER_PREFERENCE,
                ctypes.byref(DWMWCP_ROUND),
                ctypes.sizeof(DWMWCP_ROUND)
            )

            # 2. GDI RoundRect Region for hardware corner clipping (16px radius)
            if w > 10 and h > 10:
                rgn = ctypes.windll.gdi32.CreateRoundRectRgn(0, 0, w + 1, h + 1, 16, 16)
                ctypes.windll.user32.SetWindowRgn(top_hwnd, rgn, True)
        except Exception:
            pass

    def _position_window(self):
        self.window.update_idletasks()
        win_w = 304
        win_h = self.window.winfo_reqheight()
        if win_h < 150:
            win_h = 300

        screen_w = self.window.winfo_screenwidth()
        screen_h = self.window.winfo_screenheight()

        margin_x = 16
        margin_y = 56
        pos_x = screen_w - win_w - margin_x
        pos_y = screen_h - win_h - margin_y

        self.window.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")
        self._apply_native_styling(win_w, win_h)

    def _draw_progress_ring(self, canvas, cx, cy, radius, thickness, percent, track_color):
        """Draws a clean circular progress ring matching Antigravity native style."""
        outline_color = COLOR_RED if percent <= 0 else track_color
        canvas.create_oval(
            cx - radius, cy - radius,
            cx + radius, cy + radius,
            outline=outline_color,
            width=thickness
        )
        if percent > 0:
            color = "#4e7c3d" if percent >= 50 else get_status_color(percent)
            extent = - (percent / 100.0) * 359.9
            canvas.create_arc(
                cx - radius, cy - radius,
                cx + radius, cy + radius,
                start=90,
                extent=extent,
                style=tk.ARC,
                outline=color,
                width=thickness
            )

    def _render(self):
        theme = get_theme(self.theme_preference)
        self.window.configure(bg=theme["bg"])
        self.tooltips.clear()

        for widget in self.window.winfo_children():
            widget.destroy()

        main_card = tk.Frame(
            self.window,
            bg=theme["bg"],
            highlightthickness=1,
            highlightbackground=theme["border"]
        )
        main_card.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # Windows 11 Widget Header
        header = tk.Frame(main_card, bg=theme["bg"])
        header.pack(fill=tk.X, padx=14, pady=(10, 8))

        h_left = tk.Frame(header, bg=theme["bg"])
        h_left.pack(side=tk.LEFT)

        self._header_icon_img = None
        if _APP_ICON_PATH.exists():
            try:
                pil_icon = Image.open(_APP_ICON_PATH).resize((18, 18), Image.Resampling.LANCZOS)
                self._header_icon_img = ImageTk.PhotoImage(pil_icon)
            except Exception:
                pass

        if self._header_icon_img:
            icon_lbl = tk.Label(
                h_left,
                image=self._header_icon_img,
                bg=theme["bg"]
            )
            icon_lbl.image = self._header_icon_img
        else:
            icon_lbl = tk.Label(
                h_left,
                text="✦",
                font=("Segoe UI", 10),
                fg=theme["accent"],
                bg=theme["bg"]
            )
        icon_lbl.pack(side=tk.LEFT, padx=(0, 6))

        # Title and Plan Subtitle
        title_box = tk.Frame(h_left, bg=theme["bg"])
        title_box.pack(side=tk.LEFT)

        title_lbl = tk.Label(
            title_box,
            text="GravPulse",
            font=("Segoe UI", 9, "bold"),
            fg=theme["text_primary"],
            bg=theme["bg"]
        )
        title_lbl.pack(anchor="w")

        plan_name = self.cached_quota.get("plan", "Pro") if self.cached_quota else "Pro"
        email = self.cached_quota.get("email") if self.cached_quota else ""
        plan_text = f"{plan_name.upper()} PLAN"
        if email:
            short_email = email if len(email) <= 24 else email[:21] + ".."
            plan_text += f" • {short_email}"

        plan_lbl = tk.Label(
            title_box,
            text=plan_text,
            font=("Segoe UI", 6, "bold"),
            fg=theme["accent"],
            bg=theme["bg"]
        )
        """ plan_lbl.pack(anchor="w")
        if email:
            HoverTooltip(plan_lbl, f"Active Account: {email}\nPlan Tier: {plan_name}") """

        h_right = tk.Frame(header, bg=theme["bg"])
        h_right.pack(side=tk.RIGHT)

        is_online = bool(self.cached_quota and self.cached_quota.get("online"))
        is_cached = bool(self.cached_quota and self.cached_quota.get("cached"))
        has_groups = bool(self.cached_quota and self.cached_quota.get("groups"))

        # Status dot: Green = live online, Amber = cached offline, Red = offline without data
        if is_online:
            dot_color = "#6ccb5f"
        elif is_cached or has_groups:
            dot_color = "#f59e0b"  # Windows amber
        else:
            dot_color = "#ea4335"  # Red

        LabeSltexts = "🟢" if is_online else ("💾 Cached" if (is_cached or has_groups) else "🔴")
        status_dot = tk.Label(
            h_right,
            text=LabeSltexts,
            font=("Segoe UI", 8),
            fg=dot_color,
            bg=theme["bg"]
        )
        status_dot.pack(side=tk.LEFT, padx=(0, 3))

        if not is_online:
            offline_text = "Cached" if (is_cached or has_groups) else "Offline"
            off_tag = tk.Label(
                h_right,
                text=offline_text,
                font=("Segoe UI", 8),
                fg="#f59e0b" if (is_cached or has_groups) else "#ea4335",
                bg=theme["bg"]
            )
            """ off_tag.pack(side=tk.LEFT, padx=(0, 6)) """
            

        btn_refresh = tk.Label(
            h_right,
            text="↻",
            font=("Segoe UI", 10),
            fg=theme["text_secondary"],
            bg=theme["bg"],
            cursor="hand2"
        )
        btn_refresh.pack(side=tk.LEFT, padx=(0, 6))
        btn_refresh.bind("<Button-1>", lambda e: self._trigger_refresh())
        btn_refresh.bind("<Enter>", lambda e: btn_refresh.configure(fg=theme["text_primary"]))
        btn_refresh.bind("<Leave>", lambda e: btn_refresh.configure(fg=theme["text_secondary"]))

        btn_close = tk.Label(
            h_right,
            text="✕",
            font=("Segoe UI", 8),
            fg=theme["text_secondary"],
            bg=theme["bg"],
            cursor="hand2"
        )
        btn_close.pack(side=tk.LEFT)
        btn_close.bind("<Button-1>", lambda e: self.hide())
        btn_close.bind("<Enter>", lambda e: btn_close.configure(fg=theme["text_primary"]))
        btn_close.bind("<Leave>", lambda e: btn_close.configure(fg=theme["text_secondary"]))

        # Content container: If offline and NO cached data, show offline frame with 1-click launch button
        if not is_online and not has_groups:
            err_msg = self.cached_quota.get("error") if self.cached_quota else "Waiting for Antigravity..."
            if err_msg.lower() == "antigravity language_server not found or not running":
                err_msg = "Unable to authenticate with Antigravity. Please verify that Antigravity is running and try again."
            offline_frame = tk.Frame(main_card, bg=theme["bg"])
            offline_frame.pack(fill=tk.BOTH, expand=True, padx=14, pady=16)
            tk.Label(
                offline_frame,
                text="Antigravity Offline",
                font=("Segoe UI", 10, "bold"),
                fg=get_status_color(0),
                bg=theme["bg"]
            ).pack(anchor="w")
            tk.Label(
                offline_frame,
                text=err_msg,
                font=("Segoe UI", 8),
                fg=theme["text_secondary"],
                bg=theme["bg"],
                wraplength=270,
                justify="center",
            ).pack(anchor="w", pady=(4, 12))

            # Windows 11 Fluent Button (Accent Pill)
            btn_container = tk.Frame(
                offline_frame,
                bg="#005fb8" if theme.get("name") == "light" else "#60cdff",
                highlightthickness=1,
                highlightbackground="#004c99" if theme.get("name") == "light" else "#78d4ff",
                cursor="hand2",
            )
            btn_container.pack(fill=tk.X)
            

            btn_launch = tk.Label(
                btn_container,
                text="Open Antigravity",
                font=("Segoe UI", 9, "bold"),
                fg="#ffffff" if theme.get("name") == "light" else "#000000",
                bg="#005fb8" if theme.get("name") == "light" else "#60cdff",
                padx=12,
                pady=6,
                cursor="hand2"
            )
            btn_launch.pack(fill=tk.X)

            btn_bg_normal = "#005fb8" if theme.get("name") == "light" else "#60cdff"
            btn_bg_hover = "#1a6fbf" if theme.get("name") == "light" else "#78d4ff"

            def _btn_enter(e):
                btn_container.configure(bg=btn_bg_hover)
                btn_launch.configure(bg=btn_bg_hover)

            def _btn_leave(e):
                btn_container.configure(bg=btn_bg_normal)
                btn_launch.configure(bg=btn_bg_normal)

            for w in [btn_container, btn_launch]:
                w.bind("<Enter>", _btn_enter, add="+")
                w.bind("<Leave>", _btn_leave, add="+")

            def _launch_and_refresh(e=None):
                launch_antigravity()
                btn_launch.configure(text="Opening...")
                self.window.after(3000, self._trigger_refresh)

            btn_container.bind("<Button-1>", _launch_and_refresh)
            btn_launch.bind("<Button-1>", _launch_and_refresh)

            note_offline = tk.Label(
                offline_frame,
                text="* Note: When switching accounts, data from the last account may persist until Antigravity is reloaded.",
                font=("Segoe UI", 7),
                fg=theme["text_secondary"],
                bg=theme["bg"],
                wraplength=260,
                justify="left",
                anchor="w"
            )
            note_offline.pack(anchor="w", pady=(14, 0))
            return

        raw_groups = self.cached_quota.get("groups", [])
        display_groups = [(g.get("name", "Models"), g.get("buckets", [])) for g in raw_groups]

        container = tk.Frame(main_card, bg=theme["bg"])
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        def make_hover(rw, bg_def, bg_hov):
            def _enter(e):
                for w in rw:
                    try:
                        w.configure(bg=bg_hov)
                    except Exception:
                        pass
            def _leave(e):
                for w in rw:
                    try:
                        w.configure(bg=bg_def)
                    except Exception:
                        pass
            for w in rw:
                w.bind("<Enter>", _enter, add="+")
                w.bind("<Leave>", _leave, add="+")

        for g_idx, (model_name, buckets) in enumerate(display_groups):
            card_bg = theme["card_bg"]
            hover_bg = theme.get("row_hover", "#353535")

            # Windows 11 elevated card for model group
            card = tk.Frame(
                container,
                bg=card_bg,
                highlightthickness=1,
                highlightbackground=theme.get("card_border", "#363636"),
                padx=10,
                pady=8
            )
            card.pack(fill=tk.X, pady=(0, 8))

            g_lbl = tk.Label(
                card,
                text=model_name,
                font=("Segoe UI", 8, "bold"),
                fg=theme.get("group_title", "#9d9d9d"),
                bg=card_bg,
                anchor="w"
            )
            g_lbl.pack(fill=tk.X, pady=(0, 4))

            is_model_100 = len(buckets) > 0 and all(float(b.get("percent", 0.0)) >= 99.99 for b in buckets)

            if is_model_100:
                row = tk.Frame(card, bg=card_bg, cursor="hand2")
                row.pack(fill=tk.X, pady=2)

                left_col = tk.Frame(row, bg=card_bg)
                left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

                title_lbl = tk.Label(
                    left_col,
                    text="100% Available",
                    font=("Segoe UI", 9, "bold"),
                    fg=theme["text_primary"],
                    bg=card_bg,
                    anchor="w"
                )
                title_lbl.pack(fill=tk.X)

                sub_lbl = tk.Label(
                    left_col,
                    text="All limits fully refreshed",
                    font=("Segoe UI", 8),
                    fg=theme["text_secondary"],
                    bg=card_bg,
                    anchor="w"
                )
                sub_lbl.pack(fill=tk.X)

                right_col = tk.Frame(row, bg=card_bg)
                right_col.pack(side=tk.RIGHT, padx=(6, 0))

                pct_lbl = tk.Label(
                    right_col,
                    text="100%",
                    font=("Segoe UI", 9, "bold"),
                    fg=theme["text_primary"],
                    bg=card_bg
                )
                pct_lbl.pack(side=tk.LEFT, padx=(0, 4))

                row_widgets = [row, left_col, title_lbl, sub_lbl, right_col, pct_lbl]
                make_hover(row_widgets, card_bg, hover_bg)

                tip = HoverTooltip(row_widgets, f"All {model_name} limits are at 100% and fully refreshed.", theme=theme)
                self.tooltips.append(tip)

            else:
                # Limit items
                for bucket in buckets:
                    b_name = bucket.get("name", "Limit")
                    pct = bucket.get("percent", 0.0)

                    # If 5-hour limit is 100%, hide it
                    is_5h = "5" in b_name.lower() or "five" in b_name.lower() or "5" in bucket.get("id", "").lower()
                    if is_5h and float(pct) >= 99.99:
                        continue

                    row = tk.Frame(card, bg=card_bg, cursor="hand2")
                    row.pack(fill=tk.X, pady=2)

                    # Left side: Title + Resets subtitle
                    left_col = tk.Frame(row, bg=card_bg)
                    left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

                    # Check if limit is 0% depleted
                    is_depleted = float(pct) <= 0.0
                    if is_depleted:
                        clean_name = b_name.replace(" Remaining", "").strip()
                        title_text = f"{clean_name} (Exhausted)"
                        pct_fg = COLOR_RED
                    else:
                        title_text = b_name
                        pct_fg = theme["text_primary"]

                    title_lbl = tk.Label(
                        left_col,
                        text=title_text,
                        font=("Segoe UI", 9, "bold"),
                        fg=theme["text_primary"],
                        bg=card_bg,
                        anchor="w"
                    )
                    title_lbl.pack(fill=tk.X)

                    # Subtitle (e.g. "Resets in 6d 23h" or "Resets in 4h 29m")
                    countdown = bucket.get("countdown", "")
                    if countdown.lower().startswith("in "):
                        sub_text = f"Resets {countdown}"
                    elif countdown.lower() == "refreshed":
                        sub_text = "Fully refreshed"
                    elif countdown:
                        sub_text = f"Resets {countdown}"
                    else:
                        sub_text = "Fully refreshed"

                    sub_lbl = tk.Label(
                        left_col,
                        text=sub_text,
                        font=("Segoe UI", 8),
                        fg=theme["text_secondary"],
                        bg=card_bg,
                        anchor="w"
                    )
                    sub_lbl.pack(fill=tk.X)

                    # Right side: percentage text + circular ring
                    right_col = tk.Frame(row, bg=card_bg)
                    right_col.pack(side=tk.RIGHT, padx=(6, 0))

                    pct = bucket.get("percent", 0.0)
                    pct_str = f"{int(pct)}%" if pct.is_integer() else f"{pct:.1f}%"

                    pct_lbl = tk.Label(
                        right_col,
                        text=pct_str,
                        font=("Segoe UI", 9, "bold"),
                        fg=pct_fg,
                        bg=card_bg
                    )
                    pct_lbl.pack(side=tk.LEFT, padx=(0, 4))

                    # Ring indicator (shown when percent < 100)
                    ring_canvas = None
                    if pct < 100.0:
                        ring_canvas = tk.Canvas(
                            right_col,
                            width=16,
                            height=16,
                            bg=card_bg,
                            highlightthickness=0
                        )
                        ring_canvas.pack(side=tk.LEFT)
                        self._draw_progress_ring(
                            ring_canvas, 8, 8, 6, 2, pct,
                            track_color=theme["track"]
                        )

                    # Hover description tooltip setup (clean quota description only)
                    desc = bucket.get("description", "")
                    tooltip_text = desc or sub_text

                    row_widgets = [row, left_col, title_lbl, sub_lbl, right_col, pct_lbl]
                    if ring_canvas:
                        row_widgets.append(ring_canvas)

                    make_hover(row_widgets, card_bg, hover_bg)

                    tip = HoverTooltip(row_widgets, tooltip_text, theme=theme)
                    self.tooltips.append(tip)

                # New 3rd item: Full refresh date / reset ends
                weekly_bucket = next(
                    (b for b in buckets if "week" in b.get("name", "").lower() or "week" in b.get("id", "").lower()),
                    None
                )

                refresh_row = tk.Frame(card, bg=card_bg, cursor="hand2")
                refresh_row.pack(fill=tk.X, pady=2)

                ref_left = tk.Frame(refresh_row, bg=card_bg)
                ref_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

                ref_title = tk.Label(
                    ref_left,
                    text="Full Refresh Date",
                    font=("Segoe UI", 9, "bold"),
                    fg=theme["text_primary"],
                    bg=card_bg,
                    anchor="w"
                )
                ref_title.pack(fill=tk.X)

                ref_date_str = ""
                if weekly_bucket:
                    iso = weekly_bucket.get("reset_iso")
                    pct = weekly_bucket.get("percent", 100.0)
                    if iso and pct < 100.0:
                        ref_date_str = format_reset_datetime(iso)

                ref_sub_text = ref_date_str if ref_date_str else "Fully refreshed"

                ref_sub_lbl = tk.Label(
                    ref_left,
                    text=ref_sub_text,
                    font=("Segoe UI", 8),
                    fg=theme["text_secondary"],
                    bg=card_bg,
                    anchor="w",
                    wraplength=260
                )
                ref_sub_lbl.pack(fill=tk.X)

                ref_widgets = [refresh_row, ref_left, ref_title, ref_sub_lbl]
                make_hover(ref_widgets, card_bg, hover_bg)

                ref_tip_text = (
                    f"Your weekly limit will fully refresh on {ref_date_str}."
                    if ref_date_str else
                    "Your weekly quota is currently 100% refreshed."
                )
                tip = HoverTooltip(ref_widgets, ref_tip_text, theme=theme)
                self.tooltips.append(tip)

        # Bottom 1-click launcher if offline with cached data
        if not is_online:
            bottom_bar = tk.Frame(container, bg=theme["bg"])
            bottom_bar.pack(fill=tk.X, pady=(4, 0))

            btn_box = tk.Frame(
                bottom_bar,
                bg="#005fb8" if theme.get("name") == "light" else "#60cdff",
                highlightthickness=1,
                highlightbackground="#004c99" if theme.get("name") == "light" else "#78d4ff",
                cursor="hand2"
            )
            btn_box.pack(fill=tk.X)

            btn_open = tk.Label(
                btn_box,
                text="Open Antigravity",
                font=("Segoe UI", 9, "bold"),
                fg="#ffffff" if theme.get("name") == "light" else "#000000",
                bg="#005fb8" if theme.get("name") == "light" else "#60cdff",
                padx=12,
                pady=6,
                cursor="hand2"
            )
            btn_open.pack(fill=tk.X)

            btn_bg_norm = "#005fb8" if theme.get("name") == "light" else "#60cdff"
            btn_bg_hov = "#1a6fbf" if theme.get("name") == "light" else "#78d4ff"

            def _box_enter(e):
                btn_box.configure(bg=btn_bg_hov)
                btn_open.configure(bg=btn_bg_hov)

            def _box_leave(e):
                btn_box.configure(bg=btn_bg_norm)
                btn_open.configure(bg=btn_bg_norm)

            for w in [btn_box, btn_open]:
                w.bind("<Enter>", _box_enter, add="+")
                w.bind("<Leave>", _box_leave, add="+")

            def _launch_bottom(e=None):
                launch_antigravity()
                btn_open.configure(text="Opening...")
                self.window.after(3000, self._trigger_refresh)

            btn_box.bind("<Button-1>", _launch_bottom)
            btn_open.bind("<Button-1>", _launch_bottom)

        # Account switch note at bottom of popup card
        note_frame = tk.Frame(container, bg=theme["bg"])
        note_frame.pack(fill=tk.X, pady=(6, 0))

        note_lbl = tk.Label(
            note_frame,
            text="* Note: When switching accounts, data from the last account may persist until Antigravity is reloaded.",
            font=("Segoe UI", 7),
            fg=theme["text_secondary"],
            bg=theme["bg"],
            wraplength=270,
            justify="left",
            anchor="w"
        )
        note_lbl.pack(fill=tk.X)

        tip_note = HoverTooltip(
            [note_frame, note_lbl],
            "Antigravity's local language server holds credentials in memory. Reload Antigravity (Ctrl+Shift+P > Developer: Reload Window) to immediately sync newly signed-in accounts.",
            theme=theme
        )
        self.tooltips.append(tip_note)
