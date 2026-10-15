import re
import json
import urllib.request
import urllib.error
import subprocess
try:
    import psutil
except ImportError:
    psutil = None
from datetime import datetime, timezone

class AntigravityCollector:
    """Discovers local Antigravity Language Server and retrieves model rate limits / quotas."""
    def __init__(self):
        self.cached_port = None
        self.cached_token = None
        self.last_quota = None
        self.last_fetch_time = None

    def discover_credentials(self):
        """Finds language_server.exe PID, CSRF token, and listening ports via psutil or PowerShell CIM."""
        # 1. Fast native path via psutil
        if psutil is not None:
            try:
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    name = proc.info.get('name') or ''
                    if 'language_server' in name.lower():
                        cmdline_parts = proc.info.get('cmdline') or []
                        cmdline = ' '.join(cmdline_parts)
                        token_match = re.search(r'--csrf_token\s+([a-f0-9\-]+)', cmdline)
                        if token_match:
                            csrf_token = token_match.group(1)
                            ports = []
                            try:
                                conns = proc.net_connections(kind='tcp')
                                ports = [c.laddr.port for c in conns if c.status == 'LISTEN']
                            except Exception:
                                pass
                            if not ports:
                                ports = [43442, 43441]
                            return proc.info['pid'], csrf_token, ports
            except Exception:
                pass

        # 2. Fallback path via PowerShell
        try:
            create_no_window = getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000)
            ps_cmd = (
                'Get-CimInstance Win32_Process -Filter "Name = \'language_server.exe\'" '
                '| Select-Object ProcessId, CommandLine | ConvertTo-Json -Compress'
            )
            out = subprocess.check_output(
                ["powershell", "-NoProfile", "-Command", ps_cmd],
                shell=False,
                stderr=subprocess.DEVNULL,
                timeout=10,
                creationflags=create_no_window
            ).decode('utf-8', errors='ignore').strip()

            if not out:
                return None, None, []

            data = json.loads(out)
            if isinstance(data, list):
                data = data[0]

            pid = data.get("ProcessId")
            cmdline = data.get("CommandLine", "")

            token_match = re.search(r'--csrf_token\s+([a-f0-9\-]+)', cmdline)
            csrf_token = token_match.group(1) if token_match else None

            if not pid or not csrf_token:
                return None, None, []

            ports = [43442, 43441]
            try:
                port_cmd = (
                    f'Get-NetTCPConnection -OwningProcess {pid} -State Listen '
                    f'| Select-Object -ExpandProperty LocalPort | ConvertTo-Json -Compress'
                )
                port_out = subprocess.check_output(
                    ["powershell", "-NoProfile", "-Command", port_cmd],
                    shell=False,
                    stderr=subprocess.DEVNULL,
                    timeout=5,
                    creationflags=create_no_window
                ).decode('utf-8', errors='ignore').strip()
                if port_out:
                    parsed_ports = json.loads(port_out)
                    if isinstance(parsed_ports, list):
                        ports = parsed_ports
                    elif isinstance(parsed_ports, int):
                        ports = [parsed_ports]
            except Exception:
                pass

            return pid, csrf_token, ports
        except Exception:
            return None, None, []

    def request_quota_from_port(self, port, csrf_token):
        """Sends ConnectRPC request to RetrieveUserQuotaSummary."""
        url = f"http://127.0.0.1:{port}/exa.language_server_pb.LanguageServerService/RetrieveUserQuotaSummary"
        headers = {
            "Content-Type": "application/json",
            "x-codeium-csrf-token": csrf_token,
            "Connect-Protocol-Version": "1"
        }
        req = urllib.request.Request(url, data=b"{}", headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=2) as res:
            return json.loads(res.read().decode('utf-8'))

    def format_time_remaining(self, reset_time_str):
        """Calculates readable remaining time until reset from ISO string."""
        if not reset_time_str:
            return ""
        try:
            # Handle ISO string like 2026-10-14T22:42:25Z
            clean_str = reset_time_str.replace("Z", "+00:00")
            reset_dt = datetime.fromisoformat(clean_str)
            now = datetime.now(timezone.utc)
            delta = reset_dt - now
            if delta.total_seconds() <= 0:
                return "Refreshed"
            days = delta.days
            hours = (delta.seconds // 3600)
            mins = (delta.seconds % 3600) // 60
            parts = []
            if days > 0:
                parts.append(f"{days}d")
            if hours > 0:
                parts.append(f"{hours}h")
            if mins > 0 and days == 0:
                parts.append(f"{mins}m")
            return "in " + " ".join(parts) if parts else "soon"
        except Exception:
            return ""

    def get_quota(self, force_refresh=False):
        """Fetches quota using cached credentials, or auto-discovers if not cached."""
        # Try cached connection first for speed
        if not force_refresh and self.cached_port and self.cached_token:
            try:
                raw = self.request_quota_from_port(self.cached_port, self.cached_token)
                return self._parse_response(raw)
            except Exception:
                # Cache expired or process restarted
                self.cached_port = None
                self.cached_token = None

        # Discover credentials
        pid, token, ports = self.discover_credentials()
        if not token or not ports:
            return self._build_offline_fallback("Antigravity language_server not found or not running")

        for port in ports:
            try:
                raw = self.request_quota_from_port(port, token)
                self.cached_port = port
                self.cached_token = token
                return self._parse_response(raw)
            except Exception:
                continue

        return self._build_offline_fallback("Unable to connect to Antigravity RPC endpoint")

    def _build_offline_fallback(self, error_msg):
        """Constructs offline response, preserving last known quota with updated countdowns if available."""
        if self.last_quota and self.last_quota.get("groups"):
            # Deep copy groups and recalculate real-time countdowns from reset_iso
            updated_groups = []
            all_percents = []
            for g in self.last_quota.get("groups", []):
                new_buckets = []
                for b in g.get("buckets", []):
                    reset_iso = b.get("reset_iso", "")
                    new_countdown = self.format_time_remaining(reset_iso) if reset_iso else b.get("countdown", "")
                    pct = b.get("percent", 100.0)
                    if new_countdown == "Refreshed":
                        pct = 100.0
                    all_percents.append(pct)
                    new_b = dict(b)
                    new_b["countdown"] = new_countdown
                    new_b["percent"] = pct
                    new_buckets.append(new_b)
                new_g = dict(g)
                new_g["buckets"] = new_buckets
                updated_groups.append(new_g)

            lowest = min(all_percents) if all_percents else 100.0
            return {
                "online": False,
                "cached": True,
                "error": error_msg,
                "groups": updated_groups,
                "lowest_percent": lowest,
                "last_updated": self.last_quota.get("last_updated", datetime.now())
            }

        return {
            "online": False,
            "cached": False,
            "error": error_msg,
            "groups": [],
            "lowest_percent": None,
            "last_updated": datetime.now()
        }

    def _parse_response(self, raw):
        groups = []
        all_percents = []

        raw_groups = raw.get("response", {}).get("groups", [])
        for g in raw_groups:
            group_name = g.get("displayName", "Models")
            group_desc = g.get("description", "")
            buckets = []
            for b in g.get("buckets", []):
                remaining_frac = b.get("remainingFraction", 1.0)
                pct = round(remaining_frac * 100, 1)
                all_percents.append(pct)
                reset_iso = b.get("resetTime", "")
                countdown = self.format_time_remaining(reset_iso)

                buckets.append({
                    "id": b.get("bucketId", ""),
                    "name": b.get("displayName", ""),
                    "description": b.get("description", ""),
                    "window": b.get("window", ""),
                    "fraction": remaining_frac,
                    "percent": pct,
                    "reset_iso": reset_iso,
                    "countdown": countdown
                })
            groups.append({
                "name": group_name,
                "description": group_desc,
                "buckets": buckets
            })

        lowest = min(all_percents) if all_percents else 100.0
        self.last_quota = {
            "online": True,
            "error": None,
            "groups": groups,
            "lowest_percent": lowest,
            "last_updated": datetime.now()
        }
        self.last_fetch_time = datetime.now()
        return self.last_quota
