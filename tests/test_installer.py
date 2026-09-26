import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('theme', ROOT/'scripts/theme.py')
theme = importlib.util.module_from_spec(spec); spec.loader.exec_module(theme)

class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name).resolve(); self.web=self.base/'admin';self.state=self.base/'restore'
        self.target=self.web/'style/themes/lcars.css';self.target.parent.mkdir(parents=True)
        self.original=b'/* original, retain exactly */\n';self.target.write_bytes(self.original);self.target.chmod(0o640)
        self.validation=patch.object(theme,'check_upstream');self.validation.start();self.addCleanup(self.validation.stop)
    def run_action(self,action,variant='kitty-christmas',apply=True):
        return theme.run(action,self.web,self.state,variant,apply)
    def test_dry_run_is_read_only(self):
        self.run_action('install',apply=False)
        self.assertFalse(self.state.exists());self.assertEqual(self.target.read_bytes(),self.original)
    def test_round_trip_and_permissions(self):
        self.run_action('install');self.run_action('uninstall')
        self.assertEqual(self.target.read_bytes(),self.original);self.assertEqual(self.target.stat().st_mode & 0o777,0o640)
    def test_update_and_rollback(self):
        self.run_action('install');first=self.target.read_bytes()
        self.run_action('update','kitty-easter');self.assertNotEqual(first,self.target.read_bytes())
        self.run_action('rollback');self.assertEqual(first,self.target.read_bytes())
        self.run_action('rollback');self.assertEqual(self.original,self.target.read_bytes())
    def test_external_edits_preserved(self):
        self.run_action('install');self.target.write_bytes(b'upstream update')
        for action in ('update','rollback','uninstall'):
            with self.assertRaisesRegex(ValueError,'outside'):self.run_action(action)
        self.assertEqual(self.target.read_bytes(),b'upstream update')
    def test_symlink_rejected(self):
        self.target.unlink();self.target.symlink_to(ROOT/'README.md')
        with self.assertRaisesRegex(ValueError,'Symlink|symlink'):self.run_action('install')
    def test_state_inside_web_rejected(self):
        self.state=self.web/'restore'
        with self.assertRaisesRegex(ValueError,'outside'):self.run_action('install')
    def test_wrong_target_rejected(self):
        self.run_action('install');p=self.state/'state.json';s=json.loads(p.read_text());s['target']='another';p.write_text(json.dumps(s))
        with self.assertRaisesRegex(ValueError,'belong'):self.run_action('uninstall')
    def test_corrupt_backup_rejected(self):
        self.run_action('install');p=self.state/'state.json';s=json.loads(p.read_text());s['history'][0]['sha256']='invalid';p.write_text(json.dumps(s))
        with self.assertRaisesRegex(ValueError,'Corrupt'):self.run_action('uninstall')
    def test_failure_before_target_write_recovers(self):
        real=theme.atomic
        def fail(path,*args,**kwargs):
            if path==self.target:raise OSError('simulated failure')
            return real(path,*args,**kwargs)
        with patch.object(theme,'atomic',side_effect=fail):
            with self.assertRaises(OSError):self.run_action('install')
        self.run_action('recover');self.assertEqual(self.target.read_bytes(),self.original)
    def test_failure_after_target_write_recovers(self):
        real=theme.save;calls=0
        def fail(path,state):
            nonlocal calls
            calls+=1
            if calls==2:raise OSError('simulated journal commit failure')
            return real(path,state)
        with patch.object(theme,'save',side_effect=fail):
            with self.assertRaises(OSError):self.run_action('install')
        with self.assertRaisesRegex(ValueError,'recover'):self.run_action('uninstall')
        self.run_action('recover');self.assertEqual(self.target.read_bytes(),self.original)
    def test_reinstall_retains_original(self):
        self.run_action('install');self.run_action('uninstall');self.run_action('install','kitty-easter');self.run_action('uninstall')
        self.assertEqual(self.target.read_bytes(),self.original)
    def test_no_state_rejected(self):
        with self.assertRaisesRegex(ValueError,'No restore'):self.run_action('uninstall')
    def test_unsupported_upstream_refused(self):
        self.validation.stop()
        with self.assertRaisesRegex(ValueError,'regular file'):self.run_action('install')
        self.assertEqual(self.target.read_bytes(),self.original)
    def test_concurrent_mutation_rejected(self):
        with theme.locked(self.state):
            with self.assertRaisesRegex(ValueError,'running'):self.run_action('install')

if __name__=='__main__':unittest.main()
