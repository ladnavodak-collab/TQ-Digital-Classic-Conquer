import struct
import unittest
from tools.cops_account_cipher_probe import initial_keys,server_decrypt,to_server,malformed_account_packet

class AccountCipherTest(unittest.TestCase):
    def test_roundtrip_multiple_stream_boundaries(self):
        for count in [1,2,52,256,257,512,600]:
            value=bytes(i & 255 for i in range(count))
            self.assertEqual(server_decrypt(to_server(value)),value)
    def test_fixed_length_account_wire_packet(self):
        packet=malformed_account_packet()
        self.assertEqual(len(packet),52)
        self.assertEqual(struct.unpack_from("<HH",packet),(52,1051))
        self.assertNotIn(0,packet[4:20])
        self.assertNotEqual(to_server(packet),packet)
    def test_iv_is_not_constant(self):
        a,b=initial_keys()
        self.assertEqual((len(a),len(b)),(256,256))
        self.assertNotEqual(a[:32],a[32:64])
        self.assertNotEqual(a,b)
if __name__=="__main__":unittest.main()
