"""Fail-closed migration history contracts."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from migration_chain import validate_history


class ChainTests(unittest.TestCase):
    expected = [{'migration_id': '0001_namespaces.sql', 'sha256': 'a' * 64},
                {'migration_id': '0002_migration_history.json', 'sha256': 'b' * 64}]

    def test_empty_database(self):
        self.assertEqual(validate_history(self.expected, []), 0)

    def test_upgrade_prefix(self):
        self.assertEqual(validate_history(self.expected, self.expected[:1]), 1)

    def test_complete(self):
        self.assertEqual(validate_history(self.expected, self.expected), 2)

    def test_missing_predecessor(self):
        with self.assertRaisesRegex(ValueError, 'HISTORY'):
            validate_history(self.expected, self.expected[1:])

    def test_changed_source(self):
        changed = [dict(self.expected[0], sha256='c' * 64)]
        with self.assertRaisesRegex(ValueError, 'CHECKSUM'):
            validate_history(self.expected, changed)

    def test_unknown_version(self):
        with self.assertRaisesRegex(ValueError, 'HISTORY'):
            validate_history(self.expected, self.expected + [self.expected[-1]])
