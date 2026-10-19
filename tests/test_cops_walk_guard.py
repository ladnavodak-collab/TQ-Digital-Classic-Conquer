import tempfile
import unittest
from pathlib import Path
from tools.patch_cops_walk_guard import patch

ORIGINAL="""    ASSERT(aClient != nullptr);
    ASSERT(aClient->getPlayer() != nullptr);

    Client& client = *aClient;
    player.send(this); // send back...
    if (player.move(newX, newY, dir))
    {
        // broadcast the message to everyone
        player.broadcastRoomMsg(this, false);
    }"""
class WalkPatchTests(unittest.TestCase):
    def test_denies_unauthenticated_walk_before_dereferencing_player(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"src/Network/msgwalk.cpp"
            p.parent.mkdir(parents=True)
            p.write_text(ORIGINAL)
            patch(Path(d))
            got=p.read_text()
            self.assertLess(got.index("hasVerifiedGameTicket()"),got.index("Client& client = *aClient"))
            self.assertLess(got.index("aClient->getPlayer() == nullptr"),got.index("Client& client = *aClient"))
            self.assertLess(got.index("if (player.move(newX, newY, dir))"),got.index("player.send(this);"))
            self.assertNotIn("ASSERT(aClient->getPlayer() != nullptr)",got)
    def test_unknown_upstream_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"src/Network/msgwalk.cpp"
            p.parent.mkdir(parents=True)
            p.write_text("unknown upstream")
            with self.assertRaises(RuntimeError):patch(Path(d))
if __name__=="__main__":unittest.main()
