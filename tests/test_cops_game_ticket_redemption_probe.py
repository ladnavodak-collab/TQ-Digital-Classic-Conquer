import struct
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from cops_game_ticket_redemption_probe import select_dh_response,make_dh_response,make_connect
from cops_game_dh_proof_probe import transform

class TicketExchangeConstruction(unittest.TestCase):
    def test_dh_response_layout(self):
        response=make_dh_response(b"1ABDEF")
        self.assertEqual(struct.unpack_from("<i",response,7)[0],len(response)-7)
        self.assertEqual(struct.unpack_from("<i",response,11)[0],12)
        self.assertEqual(struct.unpack_from("<i",response,27)[0],6)
        self.assertEqual(response[31:],b"1ABDEF")
    def test_game_connect_frame_and_seal(self):
        frame=make_connect(78,12345)
        self.assertEqual(len(frame),36)
        self.assertEqual(struct.unpack_from("<HHii",frame),(28,1052,78,12345))
        self.assertEqual(frame[-8:],b"TQClient")
        with self.assertRaises(ValueError):
            make_connect(78,0)
    def test_shared_dh_secret_symmetry(self):
        # Simulate a server using a large prime and exponent.
        p=int("E7A69EBDF105F2A6BBDEAD7E798F76A209AD73FB466431E2E7352ED262F8C558F10BEFEA977DE9E21DCEE9B04D245F300ECCBBA03E72630556D011023F9E857F",16)
        a=pow(5,234569,p)
        params={"p":format(p,"X").encode(),"g":b"05","a":format(a,"X").encode()}
        b,key=select_dh_response(params)
        self.assertEqual(int.from_bytes(key,"big"),pow(int(b,16),234569,p))
    def test_extended_legacy_blowfish_key_roundtrip(self):
        key=bytes(range(64))
        iv=bytes(range(8))
        clear=bytes(range(75))
        crypt=transform(clear,key=key,iv=iv,encrypt=True)
        self.assertEqual(transform(crypt,key=key,iv=iv,encrypt=False),clear)
if __name__=="__main__":
    unittest.main()
