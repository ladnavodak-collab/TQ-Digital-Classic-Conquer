import struct
from pathlib import Path
import tempfile
import unittest
from tools.inspect_legacy_installer import inspect

class InstallerInspectionTests(unittest.TestCase):
    def test_minimal_pe(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/"test.exe"
            data=bytearray(256)
            data[0:2]=b"MZ"
            struct.pack_into("<I",data,0x3c,128)
            data[128:132]=b"PE\0\0"
            struct.pack_into("<H",data,132,0x14c)
            path.write_bytes(data)
            result=inspect(path,sevenzip="missing-test-7z")
            self.assertTrue(result["pe_header_valid"])
            self.assertEqual(result["pe_machine"],"0x14c")
            self.assertEqual(result["listing_status"],"7zip_not_installed")
    def test_rejects_html(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/"download.exe"
            path.write_text("<html>login</html>")
            self.assertFalse(inspect(path,sevenzip="missing-test-7z")["pe_header_valid"])
if __name__=="__main__": unittest.main()
