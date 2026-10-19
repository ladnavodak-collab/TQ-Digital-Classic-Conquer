import struct
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from cops_world_entry_probe import (
    make_enter_map,decode_enter_map,decode_mapinfo,MAP_ID,MSG_ACTION,MSG_MAPINFO
)
from cops_existing_character_relogin import parse_frames,SEAL
from cops_game_dh_proof_probe import transform
from cops_game_ticket_redemption_probe import make_connect

class WorldEntryProtocolTests(unittest.TestCase):
    def test_enter_map_wire_packet(self):
        clear=make_enter_map(123)
        self.assertEqual(len(clear),32)
        self.assertEqual(clear[-8:],b"TQClient")
        self.assertEqual(struct.unpack_from("<HH",clear),(24,MSG_ACTION))
        self.assertEqual(struct.unpack_from("<H",clear,22)[0],74)
        wire_ack=bytearray(clear[:24])
        struct.pack_into("<iHH",wire_ack,12,MAP_ID,8,8)
        self.assertEqual(decode_enter_map(bytes(wire_ack),123),(8,8))
    def test_mapinfo_and_incorrect_map_denied(self):
        frame=struct.pack("<HHIII",16,MSG_MAPINFO,MAP_ID,MAP_ID,0)
        self.assertEqual(decode_mapinfo(frame),0)
        with self.assertRaisesRegex(RuntimeError,"map"):
            decode_mapinfo(struct.pack("<HHIII",16,MSG_MAPINFO,500,500,0))
        with self.assertRaises(ValueError):
            make_enter_map(0)
    def test_map_frames_survive_tcp_fragment_boundaries(self):
        uid=123
        enter=struct.pack("<HHiIiHHHH",24,MSG_ACTION,0,uid,MAP_ID,8,8,0,74)+SEAL
        mapinfo=struct.pack("<HHIII",16,MSG_MAPINFO,MAP_ID,MAP_ID,0)+SEAL
        pieces=enter+mapinfo
        frames,offset=parse_frames(pieces[:len(enter)+6])
        self.assertEqual([typ for typ,_ in frames],[MSG_ACTION])
        self.assertEqual(offset,len(enter))
        frames,offset=parse_frames(pieces)
        self.assertEqual([typ for typ,_ in frames],[MSG_ACTION,MSG_MAPINFO])
        self.assertEqual(decode_enter_map(frames[0][1],uid),(8,8))
    def test_continue_encryption_after_transfer_token(self):
        key=bytes(range(64))
        iv=bytes(8)
        connect=make_connect(78,12345)
        packet=make_enter_map(123)
        continuous=transform(connect+packet,key=key,iv=iv,encrypt=True)
        self.assertEqual(len(continuous),len(connect)+len(packet))
        self.assertNotEqual(continuous[len(connect):],transform(packet,key=key,iv=iv,encrypt=True))
if __name__=="__main__":
    unittest.main()
