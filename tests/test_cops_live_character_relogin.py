import struct
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from cops_live_character_relogin import (
    split_frames,inspect_userinfo,SEAL,MSG_TALK,MSG_DATE,MSG_USERINFO
)

def frame(kind,payload=b""):
    return struct.pack("<HH",4+len(payload),kind)+payload+SEAL

class CharacterReLoginTests(unittest.TestCase):
    def test_partial_packet_accumulates_and_seals_checked(self):
        part1=frame(MSG_TALK,b"Welcome")
        part2=frame(MSG_DATE,bytes(32))
        messages,tail=split_frames(part1+part2[:13])
        self.assertEqual([i[0] for i in messages],[MSG_TALK])
        self.assertEqual(tail,part2[:13])
        messages,tail=split_frames(part1+part2)
        self.assertEqual([i[0] for i in messages],[MSG_TALK,MSG_DATE])
        self.assertEqual(tail,b"")
        with self.assertRaises(ValueError):
            split_frames(part1[:-1]+b"X")
    def test_rejects_oversized_or_short_header(self):
        with self.assertRaises(ValueError):
            split_frames(struct.pack("<HH",4097,MSG_TALK))
        with self.assertRaises(ValueError):
            split_frames(struct.pack("<HH",0,MSG_TALK))
    def test_userinfo_ordinal_fields_and_name(self):
        p=bytearray(96)
        struct.pack_into("<HH",p,0,len(p),MSG_USERINFO)
        struct.pack_into("<I",p,4,300000)
        struct.pack_into("<II",p,14,0,0)
        struct.pack_into("<HHHH",p,50,4,5,6,7)
        struct.pack_into("<BBBBB",p,66,1,10,1,0,1)
        p[71]=1
        p[72]=len(b"AlphaTester")
        p[73:84]=b"AlphaTester"
        result=inspect_userinfo(bytes(p))
        self.assertEqual(result["name"],"AlphaTester")
        p[18]=1
        with self.assertRaises(ValueError):inspect_userinfo(bytes(p))
if __name__=="__main__":
    unittest.main()
