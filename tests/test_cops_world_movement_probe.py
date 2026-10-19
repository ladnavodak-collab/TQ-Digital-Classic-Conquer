import struct
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from cops_world_movement_probe import make_walk,decode_walk_ack,enter_ack
from cops_world_entry_probe import MAP_ID,SEAL,MSG_ACTION

class CopsMovementProtocolTests(unittest.TestCase):
    def test_walk_is_packed_12_bytes_plus_seal(self):
        frame=make_walk(123)
        self.assertEqual(len(frame),20)
        self.assertEqual(frame[-8:],SEAL)
        self.assertEqual(struct.unpack_from("<HHIBBh",frame),(12,1005,123,6,0,0))
        self.assertTrue(decode_walk_ack(frame[:12],123))
    def test_forged_uid_and_invalid_direction_rejected(self):
        with self.assertRaises(ValueError):make_walk(0)
        with self.assertRaises(ValueError):make_walk(123,8)
        with self.assertRaises(ValueError):decode_walk_ack(make_walk(123)[:12],456)
    def test_map_ack_proves_authoritative_position(self):
        original=bytearray(struct.pack("<HHiIiHHHH",24,MSG_ACTION,1,456,MAP_ID,8,8,0,74))
        frames=[(MSG_ACTION,bytes(original))]
        self.assertTrue(enter_ack(frames,456,8,8))
        self.assertFalse(enter_ack(frames,456,9,8))
        struct.pack_into("<HH",original,16,9,8)
        self.assertTrue(enter_ack([(MSG_ACTION,bytes(original))],456,9,8))
        self.assertFalse(enter_ack([(MSG_ACTION,bytes(original))],777,9,8))
if __name__=="__main__":
    unittest.main()
