import sys
import unittest
from pathlib import Path
from src.paths import get_base_dir, get_resource_path, get_app_dir

class TestPaths(unittest.TestCase):
    def test_get_resource_path_default(self):
        p = get_resource_path("assets/ico/app.ico")
        self.assertTrue(p.exists(), f"Asset should exist at {p}")

    def test_get_resource_path_tray_asset(self):
        p = get_resource_path("assets/tray/active-64.png")
        self.assertTrue(p.exists(), f"Tray asset should exist at {p}")

    def test_frozen_simulation(self):
        original_frozen = getattr(sys, "frozen", False)
        original_meipass = getattr(sys, "_MEIPASS", None)
        try:
            sys.frozen = True
            mock_temp = Path(__file__).resolve().parent
            sys._MEIPASS = str(mock_temp)

            self.assertEqual(get_base_dir(), mock_temp)
            self.assertEqual(get_resource_path("foo.txt"), mock_temp / "foo.txt")
        finally:
            if not original_frozen and hasattr(sys, "frozen"):
                del sys.frozen
            if original_meipass is None and hasattr(sys, "_MEIPASS"):
                del sys._MEIPASS

if __name__ == "__main__":
    unittest.main()
