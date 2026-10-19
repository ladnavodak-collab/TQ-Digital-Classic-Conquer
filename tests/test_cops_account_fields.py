import tempfile
import unittest
from pathlib import Path
from tools.patch_cops_account_fields import patch

FIXTURE="""    Client& client = *aClient;
    client.setAccount(mInfo->Account);

    uint8_t seed[RC5::KEY_SIZE] =
    cipher.decrypt((uint8_t*)mInfo->Password, sizeof(mInfo->Password));

    if (isValidString(mInfo->Account) && isValidString(mInfo->Password))
        if (IS_SUCCESS(db.authenticate(client, mInfo->Account, mInfo->Password)))
        {
            fprintf(stdout, "Connection of %s on %s...\\n",
"""

class AccountValidationTests(unittest.TestCase):
    def test_unsafe_login_fields_checked_before_string_use(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"src/Network/msgaccount.cpp"
            f.parent.mkdir(parents=True)
            f.write_text(FIXTURE)
            patch(Path(d))
            s=f.read_text()
            self.assertLess(s.index("memchr(mInfo->Account"),s.index("client.setAccount"))
            self.assertLess(s.index("memchr(mInfo->Password"),s.index("client.setAccount"))
            self.assertIn("client.getStatus() != Client::NOT_AUTHENTICATED",s)
            self.assertIn("memchr(mInfo->Server",s)
            self.assertLess(s.index("db.authenticate(client"),s.index("client.setAccount"))
    def test_fails_closed_if_upstream_changes(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"src/Network/msgaccount.cpp"
            f.parent.mkdir(parents=True)
            f.write_text("different upstream")
            with self.assertRaises(RuntimeError):patch(Path(d))
if __name__=="__main__": unittest.main()
