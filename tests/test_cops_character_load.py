import tempfile
import unittest
from pathlib import Path
from tools.patch_cops_character_load import ORDERED_COLUMNS, patch

UPSTREAM = '''    static const char cmd[] =
            "SELECT * FROM `user` WHERE `account_id` = :account_id";
            uint32_t uid = (uint32_t)query.value(Player::SQLDATA_ID).toUInt();
            Player* player = new Player(aClient, uid);
    query.bindValue(":cps", player.getCPs());'''
class CharacterLoadPatchTests(unittest.TestCase):
    def test_explicit_layout_and_classic_checks_before_player_creation(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"src/Database/database.cpp"
            p.parent.mkdir(parents=True)
            p.write_text(UPSTREAM)
            patch(Path(d))
            s=p.read_text()
            self.assertNotIn("SELECT * FROM",s)
            self.assertIn(", ".join("`%s`"%c for c in ORDERED_COLUMNS),s)
            for check in ["!Entity::isPlayer(uid)","cps != 0","rebirths > 1","mapId == 0"]:
                self.assertLess(s.index(check),s.index("new Player(aClient, uid)"))
            self.assertIn('query.bindValue(":cps", 0);',s)
    def test_unknown_upstream_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"src/Database/database.cpp"
            p.parent.mkdir(parents=True)
            p.write_text("changed source")
            with self.assertRaises(RuntimeError):patch(Path(d))
if __name__=="__main__":unittest.main()
