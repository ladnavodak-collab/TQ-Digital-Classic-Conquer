import unittest
from tools.cops_game_challenge_probe import decode_structure

class GameChallengeParsingTests(unittest.TestCase):
    def test_short_challenge_rejected(self):
        with self.assertRaises(ValueError):decode_structure(b"JUNK")
    def test_missing_seal_rejected(self):
        with self.assertRaises(ValueError):decode_structure(bytes(120))
    def test_oversize_rejected(self):
        with self.assertRaises(ValueError):decode_structure(bytes(4100))
    def test_bogus_size_rejected(self):
        data=bytearray(120)
        data[-8:]=b"TQServer"
        with self.assertRaisesRegex(ValueError,"declared"):decode_structure(bytes(data))
if __name__=="__main__":unittest.main()
