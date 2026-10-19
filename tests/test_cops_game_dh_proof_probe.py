import struct
import unittest
from tools.cops_game_dh_proof_probe import transform,decode_proof,crypto_library

def fixture():
    p=b"E7A69EBDF105F2A6BBDEAD7E798F76A209AD73FB466431E2E7352ED262F8C558F10BEFEA977DE9E21DCEE9B04D245F300ECCBBA03E72630556D011023F9E857F"
    g=b"05"
    a=b"ABCD1234"
    def sized(x): return struct.pack("<i",len(x))+x
    tail=struct.pack("<i",12)+bytes(12)+sized(bytes(8))+sized(bytes(range(8)))+sized(p)+sized(g)+sized(a)+b"TQServer"
    clear=bytes(11)+struct.pack("<i",len(tail)+4)+tail
    return transform(clear,encrypt=True)

class GameProofTests(unittest.TestCase):
    def test_open_ssl_blowfish_standard_vector(self):
        # Zero-key CFB64, zero IV, zero plaintext => standard Blowfish block E_K(0).
        actual=transform(bytes(8),key=bytes(8),encrypt=True)
        self.assertEqual(actual,bytes.fromhex("4ef997456198dd78"))
    def test_structured_proof(self):
        value=decode_proof(fixture())
        self.assertEqual(value["g"],b"05")
        self.assertEqual(value["a"],b"ABCD1234")
        self.assertEqual(len(value["encrypt_iv"]),8)
    def test_rejects_wrong_seal_or_size(self):
        raw=transform(fixture())
        bad=raw[:-8]+b"Untrusted"
        with self.assertRaisesRegex(ValueError,"seal"):
            decode_proof(transform(bad,encrypt=True))
        bad=bytearray(raw)
        struct.pack_into("<i",bad,11,9000)
        with self.assertRaisesRegex(ValueError,"size"):
            decode_proof(transform(bytes(bad),encrypt=True))
    def test_rejects_non_hex_public_key(self):
        raw=transform(fixture()).replace(b"ABCD1234",b"GGGGGGGG")
        with self.assertRaisesRegex(ValueError,"hexadecimal"):
            decode_proof(transform(raw,encrypt=True))
if __name__=="__main__":
    unittest.main()
