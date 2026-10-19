import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
from tools.inventory_5039_installer import inspect_archive

class InstallerMapInventoryTests(unittest.TestCase):
    def test_finds_real_map_extensions_case_insensitive(self):
        listing = """Path = /tmp/base.exe
Type = Rar
Path = map\\map1002.DMap
Size = 123
Path = GameMap.dat
Path = scene\\palace.dds
Path = text\\readme.txt
"""
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "base.exe"
            with patch("tools.inventory_5039_installer.subprocess.run", return_value=SimpleNamespace(returncode=0,stdout=listing)):
                result = inspect_archive(path)
            self.assertEqual(result["status"], "listed")
            self.assertEqual(result["candidate_count"], 3)
            self.assertIn("map\\map1002.DMap", result["map_candidates"])
    def test_unsupported_archives_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            with patch("tools.inventory_5039_installer.subprocess.run", return_value=SimpleNamespace(returncode=2,stdout="")):
                result=inspect_archive(Path(d)/"missing.exe")
            self.assertEqual(result["status"],"not_listable")
            self.assertEqual(result["entries"],0)
if __name__=="__main__": unittest.main()
