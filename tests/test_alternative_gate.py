import copy
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from merge_preflight import assess
from install_hooks import inspect


class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.e = dict(repository='nhatnguyenvn/opc-ai-os', pr_number=2,
                      head_sha='a'*40, base_sha='b'*40, merge_sha='c'*40,
                      state='OPEN', draft=False, base_ref='main', mergeable='MERGEABLE',
                      unresolved_threads=0, review_query_complete=True, retrieval_complete=True,
                      checks=[dict(name='foundation', app_slug='github-actions', head_sha='c'*40,
                                   event='pull_request', workflow_path='.github/workflows/validate.yml',
                                   conclusion='success', status='completed')])
        self.a = {k: self.e[k] for k in ('repository','pr_number','head_sha','base_sha')}
        self.a.update(decision='APPROVED', source_reference='synthetic-test-only',
                      accepts_a1_3_exception=True, merge_method='merge')

    def test_valid_snapshot_is_not_live_authorization(self):
        self.assertEqual(assess(self.e,self.a)['status'], 'SNAPSHOT_PASS_REQUIRES_LIVE_RECHECK')

    def test_all_unsuccessful_checks_hold(self):
        for conclusion in ('failure','cancelled','skipped','neutral',None):
            with self.subTest(conclusion=conclusion):
                e=copy.deepcopy(self.e); e['checks'][0]['conclusion']=conclusion
                self.assertEqual(assess(e,self.a)['status'],'HOLD')

    def test_stale_and_incomplete_inputs_hold(self):
        for field,value in [('head_sha','d'*40),('base_sha','e'*40),('draft',True),
                            ('unresolved_threads',1),('review_query_complete',False),
                            ('retrieval_complete',False),('checks',[])]:
            with self.subTest(field=field):
                e=copy.deepcopy(self.e); e[field]=value
                self.assertEqual(assess(e,self.a)['status'],'HOLD')
        self.assertEqual(assess(self.e,{})['status'],'HOLD')


class HookTests(unittest.TestCase):
    def test_real_local_remote_pushes_and_bundle(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'source'; remote=Path(tmp)/'remote.git'
            def git(*args, ok=True):
                r=subprocess.run(['git','-C',str(root),*args],capture_output=True,text=True)
                if ok: self.assertEqual(r.returncode,0,r.stderr)
                return r
            root.mkdir(); git('init','-b','main'); git('config','user.name','Fixture')
            git('config','user.email','fixture@example.invalid'); git('config','gc.auto','0')
            (root/'.githooks').mkdir()
            shutil.copyfile(ROOT/'.githooks/pre-push',root/'.githooks/pre-push')
            git('add','.'); git('update-index','--chmod=+x','.githooks/pre-push')
            git('commit','-m','fixture')
            subprocess.run(['git','init','--bare',str(remote)],check=True,capture_output=True)
            git('remote','add','origin',str(remote)); git('push','origin','main')
            baseline=git('rev-parse','HEAD').stdout.strip()
            with self.assertRaises(ValueError): inspect(root)
            git('config','core.hooksPath','.githooks'); inspect(root)
            (root/'change.txt').write_text('change'); git('add','.'); git('commit','-m','change')
            for args in [('push','origin','main'),('push','--force','origin','HEAD:main'),
                         ('push','origin',':main')]:
                self.assertNotEqual(git(*args,ok=False).returncode,0)
                self.assertEqual(git('ls-remote','origin','refs/heads/main').stdout.split()[0],baseline)
            git('push','origin','HEAD:refs/heads/feature/fixture')
            (root/'.githooks/pre-push').write_text('changed')
            with self.assertRaises(ValueError): inspect(root)
            bundle=Path(tmp)/'baseline.bundle'; git('bundle','create',str(bundle),'main')
            git('bundle','verify',str(bundle))
            restored=Path(tmp)/'restored'
            subprocess.run(['git','clone','--branch','main',str(bundle),str(restored)],check=True,capture_output=True)
            restored_head=subprocess.check_output(['git','-C',str(restored),'rev-parse','HEAD'],text=True).strip()
            self.assertEqual(restored_head,git('rev-parse','HEAD').stdout.strip())
