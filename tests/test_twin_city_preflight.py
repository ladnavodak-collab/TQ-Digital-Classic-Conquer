import copy
import json
from pathlib import Path
import struct
import tempfile
import unittest
from tools.twin_city_preflight import validate, map_preflight

ROOT=Path(__file__).resolve().parents[1]
SAMPLE=json.loads((ROOT/"content/twin_city/twin_city_reimagined_v1.json").read_text())

class TwinCityTests(unittest.TestCase):
    def test_design_contract(self):
        self.assertEqual(validate(SAMPLE),[])
    def test_rejects_cp_and_invalid_npc(self):
        data=copy.deepcopy(SAMPLE)
        data["rules"]["conquer_points"]=True
        data["npcs"][0]["coordinates"]=[-1,4]
        self.assertTrue(any("CP and mall" in s for s in validate(data)))
        self.assertTrue(any("invalid coordinates" in s for s in validate(data)))
    def test_rejects_unearned_playability(self):
        data=copy.deepcopy(SAMPLE)
        data["releases"]["playable"]=True
        self.assertTrue(any("cannot mark playable" in s for s in validate(data)))
    def test_requires_real_gamemap(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            ini=p/"GameMap.ini"
            ini.write_text("[Map1002]\nFile=missing.dmap\n")
            self.assertTrue(map_preflight(ini,p))
            (p/"missing.dmap").write_bytes(struct.pack("<II",1003,0)+bytes(260)+struct.pack("<II",700,600))
            self.assertEqual(map_preflight(ini,p),[])
    def test_rejects_path_traversal(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            ini=p/"GameMap.ini"
            ini.write_text("[Map1002]\nFile=../outside.dmap\n")
            self.assertIn("Map1002 path escapes asset root",map_preflight(ini,p))
if __name__=="__main__": unittest.main()
