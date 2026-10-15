import sys
import time
import socket
import threading
import traceback
from pathlib import Path
import tkinter as tk
from src.collector import AntigravityCollector
from src.popup import QuotaPopupWindow
from src.tray import AntigravityTrayApp
from src.theme import apply_win32_theme
from src.notification import send_windows_toast

POLL_INTERVAL_SECONDS = 60
IPC_PORT = 43912

def ensure_single_instance():
    """Ensures only one instance of the widget runs. If another is running, sends SHOW signal."""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(('127.0.0.1', IPC_PORT))
        client.sendall(b"SHOW\n")
        client.close()
        # Successfully signaled existing instance
        sys.exit(0)
    except OSError:
        # No running instance on port, this process becomes the master
        client.close()

class AntigravityQuotaApp:
    def __init__(self):
        # Initialize Win32 process theme before GUI elements mount
        apply_win32_theme("system")

        self.collector = AntigravityCollector()
        self.root = tk.Tk()
        self.root.withdraw()  # Hidden master root

        app_ico = Path(__file__).resolve().parent / "assets" / "ico" / "app.ico"
        if app_ico.exists():
            try:
                self.root.iconbitmap(str(app_ico))
            except Exception:
                pass

        self.popup = QuotaPopupWindow(parent_root=self.root, on_refresh_callback=self.manual_refresh)
        self.tray = AntigravityTrayApp(
            collector=self.collector,
            popup_window=self.popup,
            on_exit=self.stop
        )

        self.running = True
        self.current_data = None
        self.prev_bucket_percents = {}
        self.poll_thread = None
        self.server_socket = None

        self._start_ipc_server()

    def _start_ipc_server(self):
        """Starts background TCP listener on 127.0.0.1:IPC_PORT for wake/show commands."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('127.0.0.1', IPC_PORT))
            self.server_socket.listen(5)

            def _listener():
                while self.running:
                    try:
                        conn, _ = self.server_socket.accept()
                        data = conn.recv(1024)
                        conn.close()
                        if b"SHOW" in data:
                            self.root.after(0, self._show_popup_ui)
                        elif b"NOTIFY" in data:
                            self.root.after(0, lambda: self._notify("GravPulse: Quota Refreshed", "Claude 3.5 Sonnet (5h) has refreshed to 100%!"))
                    except Exception:
                        break

            t = threading.Thread(target=_listener, daemon=True)
            t.start()
        except Exception:
            pass

    def _show_popup_ui(self):
        """Shows the popup card window."""
        if not self.current_data:
            self.current_data = self.collector.get_quota()
        self.popup.show(self.current_data)

    def manual_refresh(self):
        data = self.collector.get_quota(force_refresh=True)
        self.root.after(0, lambda: self._apply_data(data, check_notifications=False))
        return data

    def _apply_data(self, data, check_notifications=True):
        self.current_data = data
        self.tray.update_quota(data)
        self.popup.update_data(data)

        if data.get("online") or data.get("cached"):
            self._check_alerts(data, notify=check_notifications)

    def _check_alerts(self, data, notify=True):
        """Notifies user via Windows toast when quota drops below 10% or resets."""
        current_percents = {}
        for g in data.get("groups", []):
            for b in g.get("buckets", []):
                b_id = b.get("id") or b.get("name")
                b_name = b.get("name")
                pct = b.get("percent", 100.0)
                current_percents[b_id] = (b_name, pct)

                # Check if this bucket was tracked previously
                if notify and b_id in self.prev_bucket_percents:
                    prev_name, prev_pct = self.prev_bucket_percents[b_id]

                    # Condition 1: Dropped into low quota (< 10%)
                    if prev_pct >= 10.0 and pct < 10.0:
                        msg = f"{b_name} is low ({pct}% remaining). Reset: {b.get('countdown')}"
                        self._notify("GravPulse: Quota Warning", msg)

                    # Condition 2: Reset/refreshed (jumped up or reached 100% after being depleted)
                    elif pct > prev_pct + 10.0 or (pct == 100.0 and prev_pct < 100.0):
                        msg = f"{b_name} has refreshed to {pct}%!"
                        self._notify("GravPulse: Quota Refreshed", msg)

        self.prev_bucket_percents = current_percents

    def _notify(self, title, message):
        try:
            if self.tray.icon:
                self.tray.icon.notify(message, title)
        except Exception:
            pass

        try:
            threading.Thread(target=send_windows_toast, args=(title, message), daemon=True).start()
        except Exception:
            pass

    def _poll_worker(self):
        # Initial immediate fetch
        try:
            data = self.collector.get_quota()
            self.root.after(0, lambda: self._apply_data(data, check_notifications=False))
        except Exception:
            pass

        while self.running:
            for _ in range(POLL_INTERVAL_SECONDS):
                if not self.running:
                    break
                time.sleep(1)

            if not self.running:
                break

            try:
                data = self.collector.get_quota()
                self.root.after(0, lambda: self._apply_data(data, check_notifications=True))
            except Exception:
                pass

    def run(self):
        # Initial immediate fetch before starting UI loops
        try:
            init_data = self.collector.get_quota()
            self._apply_data(init_data, check_notifications=False)
        except Exception:
            init_data = {"online": False}

        tray_thread = threading.Thread(target=self.tray.run, daemon=True)
        tray_thread.start()

        self.poll_thread = threading.Thread(target=self._poll_worker, daemon=True)
        self.poll_thread.start()

        # Automatically pop up the card on launch so user immediately sees the widget
        self.root.after(300, lambda: self.popup.show(init_data))

        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception:
                pass
        try:
            self.root.quit()
        except Exception:
            pass
        sys.exit(0)

if __name__ == "__main__":
    ensure_single_instance()
    try:
        app = AntigravityQuotaApp()
        app.run()
    except Exception as e:
        log_path = Path(__file__).resolve().parent / "crash.log"
        with open(log_path, "a") as f:
            f.write(f"\n--- {time.ctime()} ---\n")
            traceback.print_exc(file=f)
        sys.exit(1)
