import tempfile
import unittest
from pathlib import Path
from tools.patch_cops_dh_trivial_keys import patch

class DHRejectionTest(unittest.TestCase):
    def test_guard_runs_before_key_agreement(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"src/Network/msgloginchallenges.cpp"
            p.parent.mkdir(parents=True)
            p.write_text("    DiffieHellman& exchange = client.getExchange();\n    string s_key = exchange.handleResponse(b_key);\n    SAFE_DELETE_ARRAY(b_key);")
            patch(Path(d))
            text=p.read_text()
            self.assertLess(text.index("first == static_cast<size_t>(b_len)"),text.index("exchange.handleResponse"))
            self.assertIn("b_key[first] == '1'",text)
            self.assertIn("SAFE_DELETE_ARRAY(b_key);\n        client.disconnect();",text)
    def test_source_drift_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"src/Network/msgloginchallenges.cpp"
            p.parent.mkdir(parents=True)
            p.write_text("missing source")
            with self.assertRaises(RuntimeError):patch(Path(d))
if __name__=="__main__":unittest.main()
