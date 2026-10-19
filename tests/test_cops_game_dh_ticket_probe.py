import struct
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from cops_game_dh_ticket_probe import (
    SERVER_SEAL, CLIENT_SEAL, parse_proof, build_exchange, connect_packet
)

def make_proof(p="10001",g="05",a="0010"):
    junk=b"wxyz"
    iv1=b"abcdefgh"
    iv2=b"12345678"
    extra=struct.pack("<i",len(junk))+junk
    extra+=struct.pack("<i",8)+iv1+struct.pack("<i",8)+iv2
    for field in (p,g,a):
        value=field.encode("ascii")
        extra+=struct.pack("<i",len(value))+value
    size=4+len(extra)+8
    return bytes(11)+struct.pack("<i",size)+extra+SERVER_SEAL

class GameDhWireTests(unittest.TestCase):
    def test_server_dh_proof_parser(self):
        p,g,a,en,de=parse_proof(make_proof())
        self.assertEqual((p,g,a),(65537,5,16))
        self.assertEqual(en,b"abcdefgh")
        self.assertEqual(de,b"12345678")
    def test_rejects_bad_seal_and_length(self):
        with self.assertRaises(ValueError):parse_proof(make_proof()[:-8]+b"NotASeal")
        with self.assertRaises(ValueError):parse_proof(make_proof()[:11]+struct.pack("<i",1)+make_proof()[15:])
    def test_dh_packet_and_derived_shared_key(self):
        with patch("cops_game_dh_ticket_probe.secrets.randbits",return_value=3):
            frame,secret=build_exchange(65537,5,16)
        self.assertEqual(secret,bytes.fromhex("1000"))
        self.assertEqual(len(frame),7+struct.unpack_from("<i",frame,7)[0])
        self.assertEqual(struct.unpack_from("<i",frame,11)[0],12)
    def test_game_connect_packet(self):
        frame=connect_packet(78,1234567)
        self.assertEqual(len(frame),36)
        self.assertEqual(frame[-8:],CLIENT_SEAL)
        self.assertEqual(struct.unpack_from("<HHii",frame),(28,1052,78,1234567))
if __name__=="__main__":unittest.main()
