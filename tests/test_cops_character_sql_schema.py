import re
import unittest
from pathlib import Path
from tools.cops_character_sql_roundtrip import COLUMNS
SCHEMA=Path(__file__).resolve().parents[1]/"db/ci_character_schema.sql"
class CharacterSchemaContract(unittest.TestCase):
    def test_positional_schema_matches_emulator_enum(self):
        sql=SCHEMA.read_text()
        user_sql=sql.split("CREATE TABLE `user` (",1)[1].split(") ENGINE=InnoDB",1)[0]
        fields=re.findall(r"^  `([a-z_]+)`\s",user_sql,re.MULTILINE)
        self.assertEqual(fields,list(COLUMNS))
    def test_classic_constraints_present(self):
        sql=SCHEMA.read_text()
        self.assertIn("CHECK (`cps` = 0)",sql)
        self.assertIn("CHECK (`metempsychosis` <= 1)",sql)
        self.assertIn("UNIQUE KEY `one_character_per_account`",sql)
        self.assertIn(") ENGINE=InnoDB AUTO_INCREMENT=1000000;",sql)
if __name__=="__main__":unittest.main()
