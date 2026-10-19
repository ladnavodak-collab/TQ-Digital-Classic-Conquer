import unittest
from unittest.mock import patch
from tools.cops_loopback_session_probe import probe

class FakeSock:
    def __init__(self, data=b"ciphertext"):
        self.data=data
        self.closed=False
    def __enter__(self): return self
    def __exit__(self,*args): self.closed=True
    def settimeout(self,*args): pass
    def recv(self,*args): return self.data

class LoopbackSessionTests(unittest.TestCase):
    def test_account_and_game_connect_and_disconnect(self):
        seen=[]
        def factory(port, timeout=2):
            seen.append(port)
            return FakeSock()
        with patch("tools.cops_loopback_session_probe.connect",side_effect=factory),patch("tools.cops_loopback_session_probe.time.sleep"):
            got=probe(3)
        self.assertEqual(got["account_connections"],3)
        self.assertEqual(got["game_connections"],3)
        self.assertEqual(got["game_handshake_bytes"],30)
        self.assertEqual(seen,[9958,5816]*3+[9958])
    def test_missing_handshake_fails(self):
        with patch("tools.cops_loopback_session_probe.connect",return_value=FakeSock(b"")):
            with self.assertRaisesRegex(RuntimeError,"exchange request"):probe(1)
    def test_rejects_unbounded_attempts(self):
        for attempts in [0,21]:
            with self.assertRaises(ValueError):probe(attempts)

if __name__=="__main__": unittest.main()
