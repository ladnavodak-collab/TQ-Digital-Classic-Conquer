import struct
import unittest
from tools.cops_game_invalid_dh_probe import invalid_dh_prefix,encrypt_prefix
class InvalidDhLengthTest(unittest.TestCase):
    def test_signed_declared_lengths(self):
        for n in (-1,0,4096,2**31-1):
            p=invalid_dh_prefix(n)
            self.assertEqual(len(p),11)
            self.assertEqual(struct.unpack_from("<i",p,7)[0],n)
    def test_out_of_range_rejected(self):
        for n in (-2**31-1,2**31):
            with self.assertRaises(ValueError):invalid_dh_prefix(n)
    def test_cipher_requires_exact_prefix(self):
        with self.assertRaises(ValueError):encrypt_prefix(b"too short")
if __name__=="__main__":unittest.main()
