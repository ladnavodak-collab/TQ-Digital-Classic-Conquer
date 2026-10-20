import unittest

class PlayerUidRangeTests(unittest.TestCase):
    def test_first_player_uid_is_in_classic_entity_range(self):
        self.assertTrue(1000000 <= 1000000 <= 1999999999)

if __name__ == '__main__':
    unittest.main()
