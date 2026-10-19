import tempfile
import unittest
from pathlib import Path
from tools.patch_cops_classic_creation import patch

HDR="err_t getPointAllot(uint16_t& aOutForce, uint16_t& aOutSpeed, uint16_t& aOutHealth, uint16_t aOutSoul,"
CPP=r"""    ASSERT_ERR(aName != nullptr && aName[0] != '\0', ERROR_INVALID_PARAMETER);

    static const char cmd[] =
    uint16_t force = 0, dexterity = 0, health = 0, soul = 0;
    getPointAllot(force, dexterity, health, soul, 1, aProfession);

    query.bindValue(":force", force);
err_t getPointAllot(uint16_t& aOutForce, uint16_t& aOutSpeed, uint16_t& aOutHealth, uint16_t aOutSoul,
"""
class ClassicCreationPatchTest(unittest.TestCase):
    def test_classic_job_and_starting_stats_guard(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            p=root/"src/Database"
            p.mkdir(parents=True)
            (p/"database.h").write_text(HDR)
            (p/"database.cpp").write_text(CPP)
            patch(root)
            body=(p/"database.cpp").read_text()
            self.assertIn("aProfession == 10",body)
            self.assertIn("aProfession == 20",body)
            self.assertIn("aProfession == 40",body)
            self.assertIn("aProfession == 100",body)
            self.assertIn("return allotErr;",body)
            self.assertLess(body.index("return allotErr;"),body.index('query.bindValue(":force", force)'))
            self.assertIn("uint16_t& aOutSoul",body)
            self.assertIn("uint16_t& aOutSoul",(p/"database.h").read_text())
    def test_upstream_drift_fails_closed(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"src/Database"
            p.mkdir(parents=True)
            (p/"database.h").write_text("unexpected upstream")
            (p/"database.cpp").write_text(CPP)
            with self.assertRaises(RuntimeError):patch(Path(t))
if __name__=="__main__":unittest.main()
