import tempfile
import unittest
from pathlib import Path
from tools.patch_cops_receive_cleanup import patch
class ReceiveCleanupTests(unittest.TestCase):
    def test_truncated_tail_releases_buffer(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"src/server.cpp"
            f.parent.mkdir()
            f.write_text("""            default:
                {
                    if (aLen < sizeof(Msg::Header))
                        return;

                    client->getCipher().decrypt(received, aLen);""")
            patch(Path(d))
            result=f.read_text()
            self.assertLess(result.index("SAFE_DELETE_ARRAY(received)"),result.index("aClient->disconnect();"))
            self.assertLess(result.index("aClient->disconnect();"),result.index("return;"))
    def test_upstream_drift_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"src/server.cpp"
            f.parent.mkdir()
            f.write_text("unexpected source")
            with self.assertRaises(RuntimeError):patch(Path(d))
if __name__=="__main__": unittest.main()
