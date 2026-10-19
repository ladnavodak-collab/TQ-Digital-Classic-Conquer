import tempfile
import unittest
from pathlib import Path
from tools.patch_cops_dh_zero_tail import patch

class DhZeroTailTests(unittest.TestCase):
    def test_clean_buffer_and_return_on_completed_dh_only(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"src/server.cpp"
            path.parent.mkdir(parents=True)
            path.write_text("                    aLen -= len;\n                    memcpy(received, ptr, aLen);")
            patch(Path(d))
            new=path.read_text()
            self.assertLess(new.index("if (aLen == 0)"),new.index("memcpy(received, ptr, aLen);"))
            self.assertIn("SAFE_DELETE_ARRAY(received);",new)
            self.assertIn("return;",new)
    def test_drift_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"src/server.cpp"
            p.parent.mkdir(parents=True)
            p.write_text("different source")
            with self.assertRaises(RuntimeError):patch(Path(d))
if __name__=="__main__":unittest.main()
