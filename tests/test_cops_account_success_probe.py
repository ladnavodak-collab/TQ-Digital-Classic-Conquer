import struct
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from cops_account_success_probe import field, request_packet, decode_response, rc5_password
from cops_account_cipher_probe import initial_keys, swap_nibbles

class AccountAuthVectors(unittest.TestCase):
    def test_packet_and_rc5_password_layout(self):
        packet=request_packet()
        self.assertEqual(len(packet),52)
        self.assertEqual(struct.unpack_from('<HH',packet),(52,1051))
        self.assertEqual(packet[4:20],field('ci_auth'))
        self.assertEqual(packet[36:52],field('TQ-CI'))
        self.assertEqual(len(rc5_password(field('CiTestPass123'))),16)
    def test_response_decoding_agrees_with_server_cipher(self):
        a,b=initial_keys()
        original=bytes(range(40))
        encoded=bytes(swap_nibbles(x^0xAB)^a[i&255]^b[(i>>8)&255] for i,x in enumerate(original))
        self.assertEqual(decode_response(encoded),original)
if __name__=='__main__':unittest.main()
