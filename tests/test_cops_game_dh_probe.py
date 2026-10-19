import struct
import unittest
from tools.cops_game_dh_probe import parse_challenge

def sample():
    parts=[b"Z"*12,b"A"*8,b"B"*8,
           b"E7A69EBDF105F2A6BBDEAD7E798F76A209AD73FB466431E2E7352ED262F8C558F10BEFEA977DE9E21DCEE9B04D245F300ECCBBA03E72630556D011023F9E857F",
           b"05",b"123ABC"]
    content=b"".join(struct.pack("<i",len(x))+x for x in parts)
    return b"P"*11+struct.pack("<i",4+len(content)+8)+content+b"TQServer"

class DhChallengeParseTest(unittest.TestCase):
    def test_valid_test_handshake(self):
        info=parse_challenge(sample())
        self.assertEqual(info["dh_generator"],5)
        self.assertTrue(info["dh_prime_bits"]>=256)
    def test_corrupted_packet_size(self):
        s=bytearray(sample())
        struct.pack_into("<i",s,11,9)
        with self.assertRaisesRegex(ValueError,"length"):parse_challenge(bytes(s))
    def test_truncated_seal(self):
        with self.assertRaises(ValueError):parse_challenge(sample()[:-2])
    def test_oversized_component(self):
        s=bytearray(sample())
        struct.pack_into("<i",s,15,5000)
        with self.assertRaisesRegex(ValueError,"field size"):parse_challenge(bytes(s))
if __name__=="__main__": unittest.main()
