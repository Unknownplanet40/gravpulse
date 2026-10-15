import winreg

THEME_DARK = {
    "name": "dark",
    "bg": "#24252a",
    "card_bg": "#2f3138",
    "card_border": "#424552",
    "row_hover": "#3b3e4a",
    "border": "#525666",
    "divider": "#3a3d49",
    "group_title": "#a8acbd",
    "text_primary": "#ffffff",
    "text_secondary": "#b0b4c4",
    "text_muted": "#828698",
    "track": "#424552",
    "accent": "#60cdff",
    "tooltip_bg": "#1c1d22",
    "tooltip_border": "#525666",
    "icon_bg": (36, 37, 42, 240),
    "icon_star": (96, 205, 255, 255),
    "icon_border": (82, 86, 102, 255)
}

THEME_LIGHT = {
    "name": "light",
    "bg": "#f3f3f3",
    "card_bg": "#ffffff",
    "card_border": "#e5e5e5",
    "row_hover": "#f7f7f7",
    "border": "#e0e0e0",
    "divider": "#e5e5e5",
    "group_title": "#5c5c5c",
    "text_primary": "#1a1a1a",
    "text_secondary": "#5c5c5c",
    "text_muted": "#8a8a8a",
    "track": "#e5e5e5",
    "accent": "#005fb8",
    "tooltip_bg": "#f9f9f9",
    "tooltip_border": "#dcdcdc",
    "icon_bg": (243, 243, 243, 240),
    "icon_star": (0, 95, 184, 255),
    "icon_border": (210, 210, 210, 255)
}

COLOR_GREEN = "#4e7c3d"
COLOR_YELLOW = "#fbbc04"
COLOR_RED = "#ea4335"
COLOR_GREY = "#434654"

RGB_GREEN = (78, 124, 61)
RGB_YELLOW = (251, 188, 4)
RGB_RED = (234, 67, 53)
RGB_GREY = (67, 70, 84)

def is_windows_dark_mode() -> bool:
    """Checks if Windows system preference is dark mode."""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        )
        val, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        return val == 0
    except Exception:
        return True

def get_theme(preference: str = "system") -> dict:
    """Returns active theme dictionary based on preference ('system', 'dark', 'light')."""
    if preference == "dark":
        return THEME_DARK
    elif preference == "light":
        return THEME_LIGHT
    else:
        return THEME_DARK if is_windows_dark_mode() else THEME_LIGHT

def get_status_color(percent):
    if percent is None or percent <= 0.0:
        return COLOR_GREY
    elif percent < 15.0:
        return COLOR_RED
    elif percent < 50.0:
        return COLOR_YELLOW
    else:
        return COLOR_GREEN

def get_rgb_status_color(percent):
    if percent is None or percent <= 0.0:
        return RGB_GREY
    elif percent < 15.0:
        return RGB_RED
    elif percent < 50.0:
        return RGB_YELLOW
    else:
        return RGB_GREEN

def apply_win32_theme(theme_preference: str = "system", hwnds: list = None):
    """Configures Win32 context menu and window dark/light theme via uxtheme and dwmapi."""
    try:
        import ctypes
        from ctypes import wintypes

        is_dark = is_windows_dark_mode() if theme_preference == "system" else (theme_preference == "dark")
        # 0 = Default, 1 = AllowDark, 2 = ForceDark, 3 = ForceLight
        mode = 2 if is_dark else 3

        uxtheme = ctypes.windll.uxtheme

        # 1. SetPreferredAppMode (Ordinal 135)
        try:
            fn_mode = uxtheme[135]
            fn_mode.argtypes = [ctypes.c_int]
            fn_mode.restype = ctypes.c_int
            fn_mode(mode)
        except Exception:
            pass

        # 2. AllowDarkModeForWindow (Ordinal 133) & DWM attributes on HWNDs
        if hwnds:
            for hwnd in hwnds:
                if not hwnd:
                    continue
                try:
                    fn_win = uxtheme[133]
                    fn_win.argtypes = [ctypes.c_void_p, ctypes.c_bool]
                    fn_win.restype = ctypes.c_bool
                    fn_win(hwnd, is_dark)
                except Exception:
                    pass

                try:
                    theme_name = "DarkMode_Explorer" if is_dark else "Explorer"
                    uxtheme.SetWindowTheme.argtypes = [wintypes.HWND, wintypes.LPCWSTR, wintypes.LPCWSTR]
                    uxtheme.SetWindowTheme(hwnd, theme_name, None)
                except Exception:
                    pass

                try:
                    dwmapi = ctypes.windll.dwmapi
                    val = ctypes.c_int(1 if is_dark else 0)
                    dwmapi.DwmSetWindowAttribute(
                        hwnd,
                        20,  # DWMWA_USE_IMMERSIVE_DARK_MODE
                        ctypes.byref(val),
                        ctypes.sizeof(val)
                    )
                except Exception:
                    pass

        # 3. FlushMenuThemes (Ordinal 136) to immediately apply to menus
        try:
            fn_flush = uxtheme[136]
            fn_flush.argtypes = []
            fn_flush.restype = None
            fn_flush()
        except Exception:
            pass

    except Exception:
        pass
