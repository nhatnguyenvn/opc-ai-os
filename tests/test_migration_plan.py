"""Offline contracts; actual rollback/replay checks require PostgreSQL."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from migration_plan import build_plan


class MigrationPlanTests(unittest.TestCase):
    def test_checksum_tracks_content(self):
        a = build_plan('0001_namespaces.sql', 'BEGIN;\nCREATE SCHEMA core;\nCOMMIT;\n')
        b = build_plan('0001_namespaces.sql', 'BEGIN;\nCREATE SCHEMA other;\nCOMMIT;\n')
        self.assertNotEqual(a['sha256'], b['sha256'])

    def test_line_endings_are_canonical(self):
        sql = 'BEGIN;\nCREATE SCHEMA core;\nCOMMIT;\n'
        self.assertEqual(build_plan('0001_namespaces.sql', sql)['sha256'],
                         build_plan('0001_namespaces.sql', sql.replace('\n', '\r\n'))['sha256'])

    def test_invalid_name_rejected(self):
        with self.assertRaises(ValueError):
            build_plan("0001_bad';.sql", 'BEGIN;\nSELECT 1;\nCOMMIT;')

    def test_missing_transaction_rejected(self):
        with self.assertRaises(ValueError):
            build_plan('0001_namespaces.sql', 'CREATE SCHEMA core;')

    def test_embedded_commit_rejected(self):
        with self.assertRaises(ValueError):
            build_plan('0001_namespaces.sql', 'BEGIN;\nCREATE SCHEMA core; COMMIT; BEGIN;\nCOMMIT;')

    def test_future_migration_requires_implementation(self):
        with self.assertRaises(ValueError):
            build_plan('0002_domain.sql', 'BEGIN;\nSELECT 1;\nCOMMIT;')
