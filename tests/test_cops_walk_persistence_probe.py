import struct
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from cops_walk_persistence_probe import walk_packet,verify_walk_echo,MSG_WALK,PLAYER_UID_MIN,PLAYER_UID_MAX
from cops_game_ticket_redemption_probe import make_connect
from cops_world_entry_probe import make_enter_map
from cops_game_dh_proof_probe import transform

class AuthenticatedWalkTests(unittest.TestCase):
    def test_walk_packet_and_response(self):
        packet=walk_packet(PLAYER_UID_MIN)
        self.assertEqual(len(packet),20)
        self.assertEqual(packet[-8:],b"TQClient")
        self.assertEqual(struct.unpack_from("<HHIBBh",packet),(12,MSG_WALK,PLAYER_UID_MIN,6,0,0))
        self.assertIsNone(verify_walk_echo(packet[:12],PLAYER_UID_MIN))
        with self.assertRaises(RuntimeError):
            verify_walk_echo(packet[:12],PLAYER_UID_MIN+1)
    def test_invalid_walking(self):
        for d in (-1,8):
            with self.assertRaises(ValueError):walk_packet(PLAYER_UID_MIN,d)
        for uid in (0, 999999, PLAYER_UID_MAX+1, 0xffffffff):
            with self.assertRaises(ValueError):walk_packet(uid)
    def test_walk_stream_continues_after_connect_and_map(self):
        key=bytes(range(64)); iv=bytes(8)
        clear=make_connect(78,12345)+make_enter_map(PLAYER_UID_MIN)
        walk=walk_packet(PLAYER_UID_MIN)
        both=transform(clear+walk,key=key,iv=iv,encrypt=True)
        self.assertEqual(len(both),len(clear)+len(walk))
        self.assertNotEqual(both[len(clear):],transform(walk,key=key,iv=iv,encrypt=True))
if __name__=="__main__":unittest.main()
