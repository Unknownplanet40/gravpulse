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
        self.cached_pid = None
        self.cached_port = None
        self.cached_token = None
        self.cached_email = None
        self.last_quota = None
        self.last_fetch_time = None

    def discover_credentials(self):
        """Finds language_server.exe PID, CSRF token, and listening ports via psutil or PowerShell CIM."""
        # 1. Fast native path via psutil
        if psutil is not None:
            try:
                candidates = []
                for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
                    name = proc.info.get('name') or ''
                    if 'language_server' in name.lower():
                        cmdline_parts = proc.info.get('cmdline') or []
                        cmdline = ' '.join(cmdline_parts)
                        token_match = re.search(r'--csrf_token\s+([a-f0-9\-]+)', cmdline)
                        if token_match:
                            candidates.append((proc, token_match.group(1)))

                # Sort newest processes first to guarantee active instance over lingering old ones
                candidates.sort(key=lambda item: item[0].info.get('create_time') or 0, reverse=True)
                for proc, csrf_token in candidates:
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
                '| Sort-Object CreationDate -Descending '
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

    def request_user_info_from_port(self, port, csrf_token):
        """Fetches account identity (email, name) and plan tier from GetUserStatus endpoint."""
        url = f"http://127.0.0.1:{port}/exa.language_server_pb.LanguageServerService/GetUserStatus"
        headers = {
            "Content-Type": "application/json",
            "x-codeium-csrf-token": csrf_token,
            "Connect-Protocol-Version": "1"
        }
        try:
            req = urllib.request.Request(url, data=b"{}", headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=1.5) as res:
                data = json.loads(res.read().decode('utf-8'))
                user_status = data.get("userStatus", {})
                email = user_status.get("email", "")
                name = user_status.get("name", "")
                plan_raw = user_status.get("planStatus", {}).get("planInfo", {}).get("planName", "")
                if not plan_raw:
                    plan_raw = user_status.get("userTier", {}).get("id", "")
                plan = self._format_plan_name(plan_raw)
                return {"email": email, "name": name, "plan": plan}
        except Exception:
            return {"email": "", "name": "", "plan": "Pro"}

    def request_plan_from_port(self, port, csrf_token):
        """Fetches user tier/plan from GetUnleashData ConnectRPC endpoint."""
        url = f"http://127.0.0.1:{port}/exa.language_server_pb.LanguageServerService/GetUnleashData"
        headers = {
            "Content-Type": "application/json",
            "x-codeium-csrf-token": csrf_token,
            "Connect-Protocol-Version": "1"
        }
        try:
            req = urllib.request.Request(url, data=b"{}", headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=1.5) as res:
                data = json.loads(res.read().decode('utf-8'))
                tier_raw = data.get("context", {}).get("properties", {}).get("userTierId", "")
                return self._format_plan_name(tier_raw)
        except Exception:
            return "Pro"

    def _format_plan_name(self, raw_tier: str) -> str:
        if not raw_tier:
            return "Pro"
        clean = raw_tier.lower()
        if "ultra" in clean:
            return "Ultra"
        if "pro" in clean:
            return "Pro"
        if "free" in clean:
            return "Free"
        if "enterprise" in clean or "team" in clean:
            return "Enterprise"
        cleaned = raw_tier.replace("g1-", "").replace("-tier", "").strip()
        return cleaned.capitalize() if cleaned else "Pro"

    def get_quota(self, force_refresh=False):
        """Fetches quota using cached credentials, or auto-discovers if not cached or account changed."""
        # 1. Try cached connection first for speed
        if not force_refresh and self.cached_port and self.cached_token and self.cached_pid:
            try:
                user_info = self.request_user_info_from_port(self.cached_port, self.cached_token)
                email = user_info.get("email")
                # Detect in-place account switch on the same language_server instance
                if email and self.cached_email and email != self.cached_email:
                    self.last_quota = None
                    self.cached_email = email
                elif email and not self.cached_email:
                    self.cached_email = email

                raw = self.request_quota_from_port(self.cached_port, self.cached_token)
                plan = user_info.get("plan") or self.request_plan_from_port(self.cached_port, self.cached_token)
                return self._parse_response(raw, plan=plan, email=self.cached_email, name=user_info.get("name"))
            except Exception:
                # Connection dropped or server restarted -> clear credentials & stale quota cache
                self.cached_port = None
                self.cached_token = None
                self.cached_pid = None
                self.last_quota = None

        # 2. Discover credentials
        pid, token, ports = self.discover_credentials()
        if not pid or not token or not ports:
            return self._build_offline_fallback("Antigravity language_server not found or not running")

        # If PID changed, purge previous process cache immediately
        if self.cached_pid and self.cached_pid != pid:
            self.last_quota = None
            self.cached_email = None

        for port in ports:
            try:
                raw = self.request_quota_from_port(port, token)
                user_info = self.request_user_info_from_port(port, token)
                email = user_info.get("email")
                if email and self.cached_email and email != self.cached_email:
                    self.last_quota = None

                plan = user_info.get("plan") or self.request_plan_from_port(port, token)
                self.cached_pid = pid
                self.cached_port = port
                self.cached_token = token
                self.cached_email = email or self.cached_email
                return self._parse_response(raw, plan=plan, email=self.cached_email, name=user_info.get("name"))
            except Exception:
                continue

        return self._build_offline_fallback("Unable to connect to Antigravity RPC endpoint")

    def _build_offline_fallback(self, error_msg):
        """Constructs offline response. Stale cache is discarded if expired (>5min) or account changed."""
        now = datetime.now()
        plan = self.last_quota.get("plan", "Pro") if self.last_quota else "Pro"
        email = self.last_quota.get("email", "") if self.last_quota else ""
        name = self.last_quota.get("name", "") if self.last_quota else ""

        # Check if cache is still valid (less than 300 seconds old if timestamp is set)
        is_cache_fresh = True
        if self.last_fetch_time is not None:
            is_cache_fresh = (now - self.last_fetch_time).total_seconds() < 300

        if is_cache_fresh and self.last_quota and self.last_quota.get("groups"):
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
                "plan": plan,
                "email": email,
                "name": name,
                "groups": updated_groups,
                "lowest_percent": lowest,
                "last_updated": self.last_quota.get("last_updated", now)
            }

        return {
            "online": False,
            "cached": False,
            "error": error_msg,
            "plan": "Pro",
            "email": "",
            "name": "",
            "groups": [],
            "lowest_percent": None,
            "last_updated": now
        }

    def _parse_response(self, raw, plan="Pro", email="", name=""):
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
            "plan": plan,
            "email": email,
            "name": name,
            "groups": groups,
            "lowest_percent": lowest,
            "last_updated": datetime.now()
        }
        self.last_fetch_time = datetime.now()
        return self.last_quota
