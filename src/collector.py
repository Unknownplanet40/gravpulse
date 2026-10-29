import os
import re
import ssl
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
        self.cached_protocol = "http"
        self.last_quota = None
        self.last_fetch_time = None

    def _extract_token_from_cmdline(self, cmdline: str) -> str | None:
        """Extracts CSRF or host bridge token with support for hyphen/underscore and equals/space."""
        if not cmdline:
            return None
        m = re.search(r'--?csrf[-_]token[=\s]+([a-zA-Z0-9_\-]+)', cmdline, re.IGNORECASE)
        if m:
            return m.group(1)
        m = re.search(r'--?host[-_]bridge[-_]token[=\s]+([a-zA-Z0-9_\-]+)', cmdline, re.IGNORECASE)
        if m:
            return m.group(1)
        return None

    def _is_antigravity_process(self, name: str, cmdline: str) -> bool:
        """Detects whether a process belongs to Antigravity or contains relevant server tokens."""
        name_lower = (name or '').lower()
        cmd_lower = (cmdline or '').lower()
        if any(kw in name_lower for kw in ['language_server', 'antigravity', 'codeium', 'gemini', 'agy']):
            return True
        if any(kw in cmd_lower for kw in ['--csrf_token', '--csrf-token', '-csrf_token', 'language_server', 'host_bridge_token']):
            return True
        return False

    def _find_ports_from_logs(self) -> list[int]:
        """Scans all Antigravity log directories for dynamically allocated HTTP/HTTPS ports."""
        ports = []
        log_dirs = [
            os.path.join(os.environ.get('APPDATA', ''), 'Antigravity', 'logs'),
            os.path.join(os.environ.get('USERPROFILE', ''), '.gemini', 'antigravity', 'logs'),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Antigravity', 'logs'),
        ]
        log_files = []
        for d in log_dirs:
            if os.path.isdir(d):
                try:
                    for fname in os.listdir(d):
                        if fname.endswith(('.log', '.txt')):
                            full_path = os.path.join(d, fname)
                            if os.path.isfile(full_path):
                                log_files.append((full_path, os.path.getmtime(full_path)))
                except Exception:
                    pass

        # Sort newest log files first
        log_files.sort(key=lambda x: x[1], reverse=True)
        for path, _ in log_files:
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                http_matches = re.findall(r'listening on random port at (\d+) for HTTP', content)
                https_matches = re.findall(r'listening on random port at (\d+) for HTTPS', content)
                gen_matches = re.findall(r'listening on (?:random )?port (?:at )?(\d+)', content)
                for match_list in [http_matches, https_matches, gen_matches]:
                    for p in reversed(match_list):
                        p_int = int(p)
                        if 1024 <= p_int <= 65535 and p_int not in ports:
                            ports.append(p_int)
            except Exception:
                pass
        return ports

    def _probe_active_endpoint(self, ports: list[int], token: str):
        """Fast-probes candidate ports to identify the live ConnectRPC port in under 400ms."""
        headers = {
            "Content-Type": "application/json",
            "x-codeium-csrf-token": token,
            "Connect-Protocol-Version": "1"
        }
        for port in ports:
            for proto in ["http", "https"]:
                url = f"{proto}://127.0.0.1:{port}/exa.language_server_pb.LanguageServerService/GetUserStatus"
                req = urllib.request.Request(url, data=b"{}", headers=headers, method="POST")
                try:
                    ctx = self._create_ssl_context() if proto == "https" else None
                    with urllib.request.urlopen(req, timeout=0.3, context=ctx) as res:
                        if res.status == 200:
                            return port, proto
                except Exception:
                    continue
        return None, None

    def discover_credentials(self):
        """Finds Antigravity language_server PID, CSRF token, and listening ports with multi-strategy auto-detect."""
        log_ports = self._find_ports_from_logs()

        # 1. Fast native path via psutil
        if psutil is not None:
            try:
                candidates = []
                for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
                    name = proc.info.get('name') or ''
                    cmdline_parts = proc.info.get('cmdline') or []
                    cmdline = ' '.join(cmdline_parts)
                    if self._is_antigravity_process(name, cmdline):
                        token = self._extract_token_from_cmdline(cmdline)
                        if token:
                            candidates.append((proc, token))

                # Sort newest processes first to guarantee active instance over lingering old ones
                candidates.sort(key=lambda item: item[0].info.get('create_time') or 0, reverse=True)
                for proc, csrf_token in candidates:
                    ports = list(log_ports)
                    try:
                        conns = proc.net_connections(kind='tcp')
                        for c in conns:
                            ip = getattr(c.laddr, 'ip', '')
                            if ip in ('127.0.0.1', '0.0.0.0', '::1', '::', ''):
                                if not c.raddr or getattr(c, 'status', '') in ('LISTEN', 'NONE', ''):
                                    if c.laddr.port not in ports:
                                        ports.append(c.laddr.port)
                    except Exception:
                        pass

                    # Also inspect parent process connections if accessible
                    try:
                        parent = proc.parent()
                        if parent:
                            for c in parent.net_connections(kind='tcp'):
                                ip = getattr(c.laddr, 'ip', '')
                                if ip in ('127.0.0.1', '0.0.0.0', '::1', '::', ''):
                                    if not c.raddr or getattr(c, 'status', '') in ('LISTEN', 'NONE', ''):
                                        if c.laddr.port not in ports:
                                            ports.append(c.laddr.port)
                    except Exception:
                        pass

                    if not ports:
                        ports = [43442, 43441]

                    # Auto-detect live endpoint by fast-probing candidate ports
                    live_port, live_proto = self._probe_active_endpoint(ports, csrf_token)
                    if live_port:
                        if live_port in ports:
                            ports.remove(live_port)
                        ports.insert(0, live_port)
                        self.cached_protocol = live_proto

                    return proc.info['pid'], csrf_token, ports
            except Exception:
                pass

        # 2. Fallback path via PowerShell CIM
        try:
            create_no_window = getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000)
            ps_cmd = (
                'Get-CimInstance Win32_Process | '
                'Where-Object { ($_.Name -match "language_server|antigravity") -or ($_.CommandLine -match "csrf") } | '
                'Sort-Object CreationDate -Descending | '
                'Select-Object ProcessId, CommandLine | ConvertTo-Json -Compress'
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
            items = data if isinstance(data, list) else [data]

            for item in items:
                pid = item.get("ProcessId")
                cmdline = item.get("CommandLine", "")
                csrf_token = self._extract_token_from_cmdline(cmdline)
                if not pid or not csrf_token:
                    continue

                ports = list(log_ports)
                try:
                    port_cmd = (
                        f'Get-NetTCPConnection -OwningProcess {pid} '
                        f'| Where-Object {{ ($_.LocalAddress -match "127\\.0\\.0\\.1|0\\.0\\.0\\.0|::") -and (-not $_.RemotePort -or $_.RemotePort -eq 0 -or $_.State -eq "Listen") }} '
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
                            for p in parsed_ports:
                                if p not in ports:
                                    ports.append(p)
                        elif isinstance(parsed_ports, int):
                            if parsed_ports not in ports:
                                ports.append(parsed_ports)
                except Exception:
                    pass

                if not ports:
                    ports = [43442, 43441]

                live_port, live_proto = self._probe_active_endpoint(ports, csrf_token)
                if live_port:
                    if live_port in ports:
                        ports.remove(live_port)
                    ports.insert(0, live_port)
                    self.cached_protocol = live_proto

                return pid, csrf_token, ports

            return None, None, []
        except Exception:
            return None, None, []

    def _create_ssl_context(self):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx

    def request_quota_from_port(self, port, csrf_token, protocol=None):
        """Sends ConnectRPC request to RetrieveUserQuotaSummary."""
        protocols = [protocol] if protocol else ([self.cached_protocol] if self.cached_protocol else ["http", "https"])
        if "http" not in protocols:
            protocols.append("http")
        if "https" not in protocols:
            protocols.append("https")

        headers = {
            "Content-Type": "application/json",
            "x-codeium-csrf-token": csrf_token,
            "Connect-Protocol-Version": "1"
        }
        last_err = None
        for proto in protocols:
            url = f"{proto}://127.0.0.1:{port}/exa.language_server_pb.LanguageServerService/RetrieveUserQuotaSummary"
            req = urllib.request.Request(url, data=b"{}", headers=headers, method="POST")
            try:
                ctx = self._create_ssl_context() if proto == "https" else None
                with urllib.request.urlopen(req, timeout=2, context=ctx) as res:
                    self.cached_protocol = proto
                    return json.loads(res.read().decode('utf-8'))
            except Exception as e:
                last_err = e
                continue
        raise last_err or ConnectionError(f"Failed to connect to port {port}")

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

    def request_user_info_from_port(self, port, csrf_token, protocol=None):
        """Fetches account identity (email, name) and plan tier from GetUserStatus endpoint."""
        protocols = [protocol] if protocol else ([self.cached_protocol] if self.cached_protocol else ["http", "https"])
        if "http" not in protocols:
            protocols.append("http")
        if "https" not in protocols:
            protocols.append("https")

        headers = {
            "Content-Type": "application/json",
            "x-codeium-csrf-token": csrf_token,
            "Connect-Protocol-Version": "1"
        }
        for proto in protocols:
            url = f"{proto}://127.0.0.1:{port}/exa.language_server_pb.LanguageServerService/GetUserStatus"
            try:
                ctx = self._create_ssl_context() if proto == "https" else None
                req = urllib.request.Request(url, data=b"{}", headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=1.5, context=ctx) as res:
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
                continue
        return {"email": "", "name": "", "plan": "Pro"}

    def request_plan_from_port(self, port, csrf_token, protocol=None):
        """Fetches user tier/plan from GetUnleashData ConnectRPC endpoint."""
        protocols = [protocol] if protocol else ([self.cached_protocol] if self.cached_protocol else ["http", "https"])
        if "http" not in protocols:
            protocols.append("http")
        if "https" not in protocols:
            protocols.append("https")

        headers = {
            "Content-Type": "application/json",
            "x-codeium-csrf-token": csrf_token,
            "Connect-Protocol-Version": "1"
        }
        for proto in protocols:
            url = f"{proto}://127.0.0.1:{port}/exa.language_server_pb.LanguageServerService/GetUnleashData"
            try:
                ctx = self._create_ssl_context() if proto == "https" else None
                req = urllib.request.Request(url, data=b"{}", headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=1.5, context=ctx) as res:
                    data = json.loads(res.read().decode('utf-8'))
                    tier_raw = data.get("context", {}).get("properties", {}).get("userTierId", "")
                    return self._format_plan_name(tier_raw)
            except Exception:
                continue
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

    def rescan(self):
        """Clears all cached process credentials and forces fresh multi-layer auto-detection."""
        self.cached_pid = None
        self.cached_port = None
        self.cached_token = None
        self.cached_email = None
        self.cached_protocol = "http"
        return self.get_quota(force_refresh=True)

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
                # Connection dropped or server closed -> clear process credentials but retain last_quota for offline fallback
                self.cached_port = None
                self.cached_token = None
                self.cached_pid = None

        # 2. Discover credentials via multi-strategy auto-detect
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
        """Constructs offline response. Preserves cached quota indefinitely until Antigravity starts again."""
        now = datetime.now()
        plan = self.last_quota.get("plan", "Pro") if self.last_quota else "Pro"
        email = self.last_quota.get("email", "") if self.last_quota else ""
        name = self.last_quota.get("name", "") if self.last_quota else ""

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
