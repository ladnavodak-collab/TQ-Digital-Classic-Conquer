import struct
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from cops_live_character_register import register_packet,CHARACTER,PROFESSION
from cops_account_success_probe import field
from cops_game_dh_proof_probe import transform
from cops_game_ticket_redemption_probe import make_connect

class RealRegisterPacketTests(unittest.TestCase):
    def test_register_packet_structure(self):
        data=register_packet()
        self.assertEqual(len(data),68)
        self.assertEqual(struct.unpack_from("<HH",data),(60,1001))
        self.assertEqual(data[4:20],field("ci_auth"))
        self.assertEqual(data[20:36],field(CHARACTER))
        self.assertEqual(struct.unpack_from("<HHi",data,52),(1003,PROFESSION,78))
        self.assertEqual(data[-8:],b"TQClient")
    def test_followup_game_cipher_keeps_cfb64_state(self):
        key=bytes(range(64))
        iv=bytes(8)
        first=make_connect(78,12345)
        second=register_packet()
        combined=transform(first+second,key=key,iv=iv,encrypt=True)
        self.assertEqual(combined[len(first):],transform(first+second,key=key,iv=iv,encrypt=True)[len(first):])
        self.assertNotEqual(combined[len(first):],transform(second,key=key,iv=iv,encrypt=True))
    def test_bad_account_rejected(self):
        with self.assertRaises(ValueError):
            register_packet(0)
if __name__=="__main__":
    unittest.main()
