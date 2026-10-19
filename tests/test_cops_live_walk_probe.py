import struct
import unittest
from tools.cops_live_walk_probe import (
    EAST,CLIENT_SEAL,make_walk,verify_walk_frame,advance_cipher
)
class WalkPacketTests(unittest.TestCase):
    def test_exact_legacy_walk_wire(self):
        packet=make_walk(1234)
        self.assertEqual(len(packet),20)
        self.assertEqual(packet[-8:],CLIENT_SEAL)
        self.assertEqual(struct.unpack_from("<HHIBBh",packet),(12,1005,1234,EAST,0,0))
        verify_walk_frame(packet[:12],1234)
    def test_invalid_player_and_direction_denied(self):
        for args in [(0,6,0),(1,8,0),(1,6,200)]:
            with self.assertRaises(ValueError):make_walk(*args)
        with self.assertRaises(RuntimeError):verify_walk_frame(make_walk(2)[:12],1)
    def test_stream_cipher_continuation(self):
        from tools.cops_game_dh_proof_probe import transform
        key=bytes(range(16))
        iv=bytes(range(8))
        before=bytes(range(32))
        packet=make_walk(12)
        result=advance_cipher(before,packet,key,iv)
        combined=transform(before+packet,key=key,iv=iv,encrypt=True)
        self.assertEqual(result,combined[len(before):])
        self.assertNotEqual(result,transform(packet,key=key,iv=iv,encrypt=True))
if __name__=="__main__":unittest.main()
