import struct
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from cops_existing_character_relogin import parse_frames, check_userinfo, SEAL, MSG_USERINFO
from cops_game_dh_proof_probe import transform

def packet(msg_type, payload):
    return struct.pack("<HH",4+len(payload),msg_type)+payload+SEAL

def sample_userinfo():
    raw=bytearray(90)
    struct.pack_into("<HHI",raw,0,90,MSG_USERINFO,123)
    struct.pack_into("<II",raw,14,0,0)
    struct.pack_into("<7H",raw,50,4,5,6,7,0,192,35)
    raw[66]=1
    raw[67]=10
    raw[69]=0
    raw[72:72+len(b"AlphaTester")]=b"AlphaTester"
    return bytes(raw)

class CharacterRelogProtocolTests(unittest.TestCase):
    def test_two_messages_with_chunk_boundary(self):
        first=packet(1004,b"welcome")
        second=sample_userinfo()+SEAL
        complete=first+second
        decoded,used=parse_frames(complete[:len(first)+12])
        self.assertEqual([typ for typ,_ in decoded],[1004])
        self.assertEqual(used,len(first))
        decoded,used=parse_frames(complete)
        self.assertEqual([typ for typ,_ in decoded],[1004,MSG_USERINFO])
        self.assertEqual(used,len(complete))
        self.assertEqual(check_userinfo(decoded[1][1]),123)
    def test_decrypt_continuous_ciphertext_stream(self):
        raw=packet(1004,b"hello")+sample_userinfo()+SEAL
        key=bytes(range(64))
        iv=bytes(8)
        wire=transform(raw,key=key,iv=iv,encrypt=True)
        restored=transform(wire,key=key,iv=iv,encrypt=False)
        frames,used=parse_frames(restored)
        self.assertEqual(used,len(raw))
        self.assertEqual(check_userinfo(frames[1][1]),123)
    def test_reject_bad_seal_and_classic_stats(self):
        packet_bytes=packet(1004,b"hello")
        with self.assertRaisesRegex(RuntimeError,"seal"):
            parse_frames(packet_bytes[:-1]+b"X")
        broken=bytearray(sample_userinfo())
        struct.pack_into("<I",broken,18,1)
        with self.assertRaisesRegex(RuntimeError,"attributes"):
            check_userinfo(bytes(broken))
    def test_reject_invalid_length_and_truncated_fields(self):
        with self.assertRaisesRegex(RuntimeError,"header"):
            parse_frames(struct.pack("<HH",1,1004)+b"abcde")
        with self.assertRaisesRegex(RuntimeError,"truncated"):
            check_userinfo(b"short")
if __name__=="__main__":
    unittest.main()
