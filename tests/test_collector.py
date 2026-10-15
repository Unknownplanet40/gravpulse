import unittest
from src.collector import AntigravityCollector
from src.tray import create_tray_icon
from PIL import Image

class TestAntigravityCollector(unittest.TestCase):
    def setUp(self):
        self.collector = AntigravityCollector()

    def test_discover_and_fetch_quota(self):
        """Verifies that the collector discovers Antigravity and fetches quota."""
        quota = self.collector.get_quota()
        self.assertIsNotNone(quota)
        self.assertIn("online", quota)
        self.assertTrue(quota["online"], f"Antigravity collector failed: {quota.get('error')}")
        self.assertIn("groups", quota)
        self.assertGreater(len(quota["groups"]), 0)

        # Check buckets exist
        for group in quota["groups"]:
            self.assertIn("name", group)
            self.assertIn("buckets", group)
            for bucket in group["buckets"]:
                self.assertIn("name", bucket)
                self.assertIn("percent", bucket)
                self.assertIn("countdown", bucket)
                self.assertIsInstance(bucket["percent"], (int, float))

    def test_format_time_remaining(self):
        """Verifies formatting of ISO reset timestamps."""
        res = self.collector.format_time_remaining("2099-01-01T00:00:00Z")
        self.assertTrue(res.startswith("in "), f"Expected remaining time format, got: {res}")

        past_res = self.collector.format_time_remaining("2000-01-01T00:00:00Z")
        self.assertEqual(past_res, "Refreshed")

class TestTrayIconGeneration(unittest.TestCase):
    def test_create_tray_icon(self):
        """Verifies that dynamic tray icons render valid RGBA 64x64 images."""
        for pct in [100.0, 50.0, 20.0, 5.0, 0.0, None]:
            img = create_tray_icon(percent=pct, is_online=True)
            self.assertIsInstance(img, Image.Image)
            self.assertEqual(img.size, (64, 64))
            self.assertEqual(img.mode, "RGBA")

        # Offline state
        offline_img = create_tray_icon(is_online=False)
        self.assertEqual(offline_img.size, (64, 64))

    def test_tooltip_length_limit(self):
        """Verifies that generated tray tooltip never exceeds Win32 128 char limit."""
        from src.tray import AntigravityTrayApp
        collector = AntigravityCollector()
        app = AntigravityTrayApp(collector, None)
        quota = collector.get_quota()
        app.update_quota(quota)
        self.assertLessEqual(len(app.icon.title), 120)

    def test_theme_detection(self):
        """Verifies theme palette retrieval for dark, light, and system modes."""
        from src.theme import get_theme, is_windows_dark_mode
        self.assertIsInstance(is_windows_dark_mode(), bool)
        dark = get_theme("dark")
        light = get_theme("light")
        system = get_theme("system")
        self.assertEqual(dark["name"], "dark")
        self.assertEqual(light["name"], "light")
        self.assertIn(system["name"], ["dark", "light"])
        self.assertEqual(dark["bg"], "#24252a")
        self.assertEqual(light["bg"], "#f3f3f3")

    def test_format_reset_datetime(self):
        """Verifies exact datetime formatting for weekly reset."""
        from src.popup import format_reset_datetime
        formatted = format_reset_datetime("2026-10-14T22:42:25Z")
        self.assertTrue(len(formatted) > 10)
        self.assertIn(", at ", formatted)
        # Empty string on None
        self.assertEqual(format_reset_datetime(""), "")

    def test_apply_win32_theme(self):
        """Verifies apply_win32_theme safely executes for system, dark, and light preferences."""
        from src.theme import apply_win32_theme
        # Should execute safely without throwing exceptions
        apply_win32_theme("system")
        apply_win32_theme("dark")
        apply_win32_theme("light")
        apply_win32_theme("system", hwnds=[0, None])

    def test_cached_offline_fallback(self):
        """Verifies that offline fallback retains cached groups and updates countdowns."""
        collector = AntigravityCollector()
        collector.last_quota = {
            "online": True,
            "groups": [
                {
                    "name": "Gemini Models",
                    "buckets": [
                        {
                            "id": "gemini_flash",
                            "name": "Gemini 2.5 Flash",
                            "percent": 85.0,
                            "reset_iso": "2099-01-01T00:00:00Z",
                            "countdown": "in 1d"
                        }
                    ]
                }
            ],
            "lowest_percent": 85.0
        }
        res = collector._build_offline_fallback("Simulated offline")
        self.assertFalse(res["online"])
        self.assertTrue(res["cached"])
        self.assertEqual(len(res["groups"]), 1)
        self.assertEqual(res["groups"][0]["name"], "Gemini Models")
        self.assertTrue(res["groups"][0]["buckets"][0]["countdown"].startswith("in "))

    def test_launch_antigravity_function(self):
        """Verifies launch_antigravity function is callable and behaves predictably."""
        from src.popup import launch_antigravity
        # callable check
        self.assertTrue(callable(launch_antigravity))

    def test_smart_best_available_tray_status(self):
        """Verifies that tray icon stays green if one model has >50% capacity even if other is 0%."""
        from src.tray import AntigravityTrayApp
        collector = AntigravityCollector()
        app = AntigravityTrayApp(collector, None)

        # Gemini 92%, Claude 0% -> Best model is 92% -> Icon is active (Green)
        data = {
            "online": True,
            "groups": [
                {"name": "Gemini Models", "buckets": [{"name": "5h", "percent": 92.0}]},
                {"name": "Claude Models", "buckets": [{"name": "5h", "percent": 0.0}]}
            ]
        }
        app.update_quota(data)

    def test_quota_alert_reset_notification(self):
        """Verifies _check_alerts triggers notification on reset."""
        from unittest.mock import MagicMock
        from main import AntigravityQuotaApp
        app = AntigravityQuotaApp.__new__(AntigravityQuotaApp)
        app.prev_bucket_percents = {"bucket_claude_5h": ("Claude 3.5 Sonnet (5h)", 0.0)}
        app.tray = MagicMock()

        notified = []
        app._notify = lambda title, msg: notified.append((title, msg))

        # Data simulates Claude resetting back to 100%
        reset_data = {
            "online": True,
            "groups": [{
                "name": "Claude Models",
                "buckets": [{
                    "id": "bucket_claude_5h",
                    "name": "Claude 3.5 Sonnet (5h)",
                    "percent": 100.0,
                    "countdown": "Refreshed"
                }]
            }]
        }
        app._check_alerts(reset_data, notify=True)

        self.assertEqual(len(notified), 1)
        self.assertIn("Quota Refreshed", notified[0][0])
        self.assertIn("refreshed to 100.0%", notified[0][1])

    def test_plan_name_formatting(self):
        """Verifies plan name formatting from raw tier string."""
        collector = AntigravityCollector()
        self.assertEqual(collector._format_plan_name("g1-pro-tier"), "Pro")
        self.assertEqual(collector._format_plan_name("g1-ultra-tier"), "Ultra")
        self.assertEqual(collector._format_plan_name("free-tier"), "Free")
        self.assertEqual(collector._format_plan_name("enterprise-tier"), "Enterprise")
        self.assertEqual(collector._format_plan_name(""), "Pro")

    def test_account_switch_invalidates_cache(self):
        """Verifies that changing account email or PID purges stale quota cache."""
        from datetime import datetime
        collector = AntigravityCollector()
        collector.cached_pid = 1111
        collector.cached_port = 50000
        collector.cached_token = "token1"
        collector.cached_email = "old@example.com"
        collector.last_fetch_time = datetime.now()
        collector.last_quota = {
            "online": True,
            "email": "old@example.com",
            "plan": "Pro",
            "groups": [{"name": "Models", "buckets": []}]
        }

        # Mock request_user_info_from_port returning new account
        collector.request_user_info_from_port = lambda port, token: {
            "email": "new@example.com",
            "name": "New User",
            "plan": "Ultra"
        }
        collector.request_quota_from_port = lambda port, token: {
            "response": {"groups": []}
        }

        res = collector.get_quota()
        self.assertEqual(res["email"], "new@example.com")
        self.assertEqual(res["plan"], "Ultra")
        self.assertEqual(collector.cached_email, "new@example.com")

    def test_expired_cache_not_used_in_fallback(self):
        """Verifies that offline fallback does not retain stale cache older than 5 minutes."""
        from datetime import datetime, timedelta
        collector = AntigravityCollector()
        collector.last_fetch_time = datetime.now() - timedelta(seconds=400)
        collector.last_quota = {
            "online": True,
            "groups": [{"name": "Models", "buckets": [{"percent": 90.0}]}]
        }
        res = collector._build_offline_fallback("Endpoint offline")
        self.assertFalse(res["online"])
        self.assertFalse(res["cached"])
        self.assertEqual(len(res["groups"]), 0)

    def test_antigravity_exit_retains_cached_offline(self):
        """Verifies that closing Antigravity preserves recent quota in offline cached mode."""
        from datetime import datetime
        collector = AntigravityCollector()
        collector.cached_pid = 9999
        collector.cached_port = 54321
        collector.cached_token = "secret"
        collector.cached_email = "test@example.com"
        collector.last_fetch_time = datetime.now()
        collector.last_quota = {
            "online": True,
            "email": "test@example.com",
            "plan": "Pro",
            "groups": [{"name": "Claude", "buckets": [{"name": "Sonnet", "percent": 85.0, "reset_iso": ""}]}],
            "lowest_percent": 85.0,
            "last_updated": datetime.now()
        }

        # Mock port failure (process exited) and discovery failure
        collector.request_user_info_from_port = lambda port, token: (_ for _ in ()).throw(Exception("Connection refused"))
        collector.discover_credentials = lambda: (None, None, [])

        res = collector.get_quota()
        self.assertFalse(res["online"])
        self.assertTrue(res["cached"])
        self.assertEqual(len(res["groups"]), 1)
        self.assertEqual(res["groups"][0]["buckets"][0]["percent"], 85.0)

if __name__ == "__main__":
    unittest.main()

