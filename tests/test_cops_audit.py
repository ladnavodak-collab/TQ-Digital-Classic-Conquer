import tempfile
import unittest
from pathlib import Path
from tools.audit_cops import scan

class AuditTests(unittest.TestCase):
    def _fixture(self, config: str, database: str):
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        (root / "data").mkdir()
        (root / "src" / "Database").mkdir(parents=True)
        (root / "data" / "settings.cfg").write_text(config, encoding="utf-8")
        (root / "src" / "Database" / "database.cpp").write_text(database, encoding="utf-8")
        self.addCleanup(tmp.cleanup)
        return root

    def test_flags_insecure_upstream_patterns(self):
        root = self._fixture("SQL_USER = root\nSQL_PWD = root\n",
            "if (password.compare(aPassword) == 0) {}\n"
            'LOG(DBG, "Executing SQL: %s", qPrintable(getSqlCommand(query)));\n')
        self.assertEqual({f.rule for f in scan(root)},
                         {"COPS001", "COPS002", "COPS003", "COPS004"})

    def test_clean_configuration_has_no_alerts(self):
        root = self._fixture("SQL_USER = game_app\nSQL_PWD = ${INJECT_AT_RUNTIME}\n",
                             "verify_password_hash(hash, supplied);\n")
        self.assertEqual(scan(root), [])

    def test_missing_files_are_reported_as_incomplete(self):
        with tempfile.TemporaryDirectory() as directory:
            result = scan(Path(directory))
        self.assertEqual(len(result), 2)
        self.assertTrue(all(f.rule == "COPS000" for f in result))

    def test_does_not_expose_secret_values_in_description(self):
        root = self._fixture("SQL_PWD = root\n", "")
        combined = "\n".join(str(f) for f in scan(root))
        self.assertNotIn("SQL_PWD = root", combined)

if __name__ == "__main__":
    unittest.main()
