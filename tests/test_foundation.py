"""Phase A negative acceptance cases run against isolated Git repositories."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from validate import validate, check_schema
from release_manifest import generate


class FoundationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'repo'
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns('.git', '__pycache__', '.env', '*.pyc', 'tmp'))
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        # Disposable repositories must not leave detached writers racing cleanup.
        subprocess.run(['git', '-C', str(self.root), 'config', 'maintenance.auto', 'false'], check=True)
        subprocess.run(['git', '-C', str(self.root), 'config', 'gc.auto', '0'], check=True)

    def change(self, path, fn):
        target = self.root / path
        data = json.loads(target.read_text(encoding='utf-8'))
        fn(data)
        target.write_text(json.dumps(data), encoding='utf-8')

    def fails(self, reason):
        errors = validate(self.root)
        self.assertTrue(any(reason in error for error in errors), errors)
        result = subprocess.run([sys.executable, str(self.root / 'scripts/validate.py')], capture_output=True)
        self.assertNotEqual(result.returncode, 0)

    def test_baseline(self):
        self.assertEqual(validate(self.root), [])

    def test_A_TEST_001_missing_constitution(self):
        (self.root / 'constitution/v1.0/constitution.yaml').unlink()
        self.fails('constitution/v1.0/constitution.yaml')

    def test_A_TEST_002_duplicate_control(self):
        self.change('runtime/hard-controls/v1.0/controls.yaml', lambda d: d['controls'].append(d['controls'][0]))
        self.fails('duplicate control ID')

    def test_A_TEST_003_runtime_dependency(self):
        self.change('agents/sales/manifest.yaml', lambda d: d.update(requires_runtime='9.0.0'))
        self.fails('invalid runtime dependency')

    def test_A_TEST_004_secret_committed(self):
        path = self.root / '.env'
        path.write_text('TOKEN=' + 'gh' + 'p_' + 'x' * 36)
        subprocess.run(['git', '-C', str(self.root), 'add', '-f', '.env'], check=True)
        self.fails('secret pattern detected')

    def test_A_TEST_005_permission_reference(self):
        self.change('agents/sales/manifest.yaml', lambda d: d.update(permission_profile_id='PERM-MISSING-001'))
        self.fails('broken permission reference')

    def test_A_TEST_006_environment(self):
        self.change('config/production/environment.yaml', lambda d: d.update(environment='test'))
        self.fails('invalid environment mapping')

    def test_A_TEST_007_manifest_version(self):
        self.change('release/manifest.template.yaml', lambda d: d['agents'][0].update(version='1.1.0'))
        self.fails('release manifest version mismatch')

    def test_A_TEST_008_missing_finance(self):
        self.change('release/manifest.template.yaml', lambda d: d.update(agents=[a for a in d['agents'] if a['id'] != 'AGENT-FINANCE-001']))
        self.fails('missing required package')

    def test_malformed_json(self):
        (self.root / 'agents/finance/manifest.yaml').write_text('{invalid')
        self.fails('malformed configuration')

    def test_missing_required_field(self):
        self.change('agents/finance/manifest.yaml', lambda d: d.pop('name'))
        self.fails('missing required field name')

    def test_invalid_enum(self):
        self.change('agents/finance/manifest.yaml', lambda d: d.update(status='ACTIVE'))
        self.fails('invalid enum')

    def test_reference_escape(self):
        self.change('agents/finance/manifest.yaml', lambda d: d.update(output_contract='../outside.yaml'))
        self.fails('outside repository')

    def test_production_activation(self):
        self.change('config/production/environment.yaml', lambda d: d.update(execution_enabled=True))
        self.fails('invalid constant')

    def test_p0_downgrade_blocked(self):
        self.change('runtime/hard-controls/v1.0/controls.yaml', lambda d: d['controls'][0].update(severity='P1'))
        self.fails('approved control set or severity changed')

    def test_duplicate_json_keys(self):
        (self.root / 'fixtures/invalid.json').write_text('{"id":"X","id":"Y"}')
        self.fails('malformed configuration')

    def test_schema_rejects_unknown_keyword(self):
        errors = []
        check_schema({}, {'unsupported': True}, 'test', errors)
        self.assertTrue(errors)

    def test_manifest_blocks_uncommitted_tree(self):
        with self.assertRaisesRegex(ValueError, 'Clean committed'):
            generate(self.root)

    def test_manifest_binds_exact_commit_without_approval(self):
        subprocess.run(['git', '-C', str(self.root), 'add', '.'], check=True, capture_output=True)
        subprocess.run(['git', '-C', str(self.root), '-c', 'user.name=Test Fixture',
                        '-c', 'user.email=fixture@localhost', 'commit', '-qm', 'fixture'], check=True)
        manifest = generate(self.root)
        commit = subprocess.check_output(['git', '-C', str(self.root), 'rev-parse', 'HEAD'], text=True).strip()
        self.assertEqual(manifest['build_commit'], commit)
        self.assertIsNone(manifest['approval_reference'])
        self.assertFalse(manifest['go_live'])
        self.assertEqual(manifest['status'], 'BUILD_ONLY_NOT_DEPLOYABLE')
        self.assertIn('constitution/v1.0/constitution.yaml', manifest['artifact_hashes'])


if __name__ == '__main__':
    unittest.main()
