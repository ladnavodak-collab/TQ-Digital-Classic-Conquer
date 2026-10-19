import struct
import tempfile
import unittest
from pathlib import Path
from tools.make_synthetic_cops_dmap import make_map,write_fixture

class SyntheticDMapTests(unittest.TestCase):
    def test_checksums_match_cops_formula(self):
        width,height=9,7
        raw=make_map(width,height)
        self.assertEqual(struct.unpack_from("<II",raw,268),(width,height))
        offset=276
        for y in range(height):
            checksum=0
            for x in range(width):
                mask,terrain,alt=struct.unpack_from("<HHh",raw,offset)
                checksum+=mask*(terrain+y+1)+(alt+2)*(x+1+terrain)
                offset+=6
            self.assertEqual(struct.unpack_from("<I",raw,offset)[0],checksum)
            offset+=4
        self.assertEqual(struct.unpack_from("<ii",raw,offset),(0,0))
        self.assertEqual(len(raw),offset+8)
    def test_rejects_out_of_bounds_dimensions(self):
        for dims in [(0,16),(1,16),(129,2)]:
            with self.assertRaises(ValueError): make_map(*dims)
    def test_writes_matching_ini_reference(self):
        with tempfile.TemporaryDirectory() as d:
            root=write_fixture(Path(d))
            self.assertIn("File=tq-ci-1002.dmap",(root/"GameMap.ini").read_text())
            self.assertTrue((root/"tq-ci-1002.dmap").is_file())
if __name__=="__main__":
    unittest.main()
