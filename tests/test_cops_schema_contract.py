import unittest
from tools.cops_schema_contract import verify

SOURCE = ' '.join('FROM `' + n + '`' for n in
    ("map","itemtype","npc","monstertype","generator","magictype"))
SCHEMA = ' '.join('CREATE TABLE IF NOT EXISTS `' + n + '` (' for n in
    ("map","itemtype","npc","monstertype","generator","magictype"))
SCHEMA += ' ' + ' '.join('`' + n + '` INT' for n in
    ("id","doc_id","type","weather","portal_x","portal_y","reborn_map","reborn_portal","light"))

class LoaderSchemaContractTests(unittest.TestCase):
    def test_valid_contract(self):
        self.assertEqual(verify(SOURCE, SCHEMA), [])
    def test_detects_missing_table(self):
        result = verify(SOURCE, SCHEMA.replace('CREATE TABLE IF NOT EXISTS `npc`', 'BROKEN'))
        self.assertIn("missing schema table: npc", result)
    def test_detects_upstream_drift(self):
        result = verify(SOURCE.replace('FROM `map`','FROM `game_map`'),SCHEMA)
        self.assertIn("upstream loader query not found: map",result)
    def test_detects_missing_map_column(self):
        result = verify(SOURCE,SCHEMA.replace('`doc_id` INT','`doc_id` TEXT'))
        self.assertIn("missing map column: doc_id",result)

if __name__=="__main__":
    unittest.main()
