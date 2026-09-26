"""Exercise the downloaded runner as a separate shell process, with no network."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('builder',ROOT/'scripts/build_runner.py')
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)

class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name).resolve();self.pkg=self.base/'package';self.web=self.base/'test admin';self.state=self.base/'private restore'
        for name in builder.FILES:
            dest=self.pkg/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,dest)
        shutil.copyfile(ROOT/'VERSION',self.pkg/'VERSION')
        shutil.copyfile(ROOT/'LICENSE',self.pkg/'LICENSE')
        shutil.copyfile(ROOT/'ARTWORK-NOTICE.md',self.pkg/'ARTWORK-NOTICE.md')
        fixture=self.web/'index.lp';fixture.parent.mkdir(parents=True);fixture.write_bytes(b'isolated upstream fixture')
        (self.pkg/'docs/upstream-lock.json').write_text(json.dumps({'files':{'index.lp':hashlib.sha256(fixture.read_bytes()).hexdigest()}}))
        self.target=self.web/'style/themes/lcars.css';self.target.parent.mkdir(parents=True);self.target.write_bytes(b'original lcars\n')
        self.runner=self.base/'downloaded-runner.sh';self.build()
    def build(self):
        old=builder.ROOT
        try:
            builder.ROOT=self.pkg;self.runner.write_text(builder.render())
        finally:builder.ROOT=old
    def invoke(self,*args,pipe=False):
        extra=['--web-root',str(self.web),'--state-dir',str(self.state)]
        command=['sh','-s','--',*args,*extra] if pipe else ['sh',str(self.runner),*args,*extra]
        return subprocess.run(command,input=self.runner.read_text() if pipe else None,text=True,capture_output=True)
    def test_every_season_round_trip(self):
        for season in ('kitty-christmas','kitty-easter','kitty-beach-summer','kitty-halloween-fall'):
            with self.subTest(season=season):
                r=self.invoke('install','--theme',season,'--apply')
                self.assertEqual(r.returncode,0,r.stderr)
                self.assertIn(season.encode(),self.target.read_bytes())
                r=self.invoke('upgrade','--apply')
                self.assertEqual(r.returncode,0,r.stderr)
                self.assertIn('Theme: '+season,r.stdout)
                r=self.invoke('uninstall','--apply')
                self.assertEqual(r.returncode,0,r.stderr)
                self.assertEqual(self.target.read_bytes(),b'original lcars\n')
    def test_help_without_action(self):
        r=subprocess.run(['sh',str(self.runner)],text=True,capture_output=True)
        self.assertEqual(r.returncode,0,r.stderr);self.assertIn('dry-run',r.stdout);self.assertFalse(self.state.exists())
    def test_pipe_dry_run_and_paths_with_spaces(self):
        r=self.invoke('install',pipe=True)
        self.assertEqual(r.returncode,0,r.stderr);self.assertIn('DRY RUN',r.stdout)
        self.assertEqual(self.target.read_bytes(),b'original lcars\n');self.assertFalse(self.state.exists())
    def test_install_upgrade_preserves_light_theme_and_offline_uninstall(self):
        self.assertEqual(self.invoke('install','--theme','kitty-easter','--apply').returncode,0)
        css=self.pkg/'dist/kitty-easter.css';css.write_text(css.read_text()+'\n/* updated package */\n');self.build()
        r=self.invoke('upgrade','--apply');self.assertEqual(r.returncode,0,r.stderr)
        self.assertIn('Theme: kitty-easter',r.stdout);self.assertIn(b'updated package',self.target.read_bytes())
        shutil.rmtree(self.pkg) # A downloaded runner needs no source checkout.
        r=self.invoke('uninstall','--apply');self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(self.target.read_bytes(),b'original lcars\n')
    def test_theme_switch_and_rollback(self):
        self.assertEqual(self.invoke('install','--apply').returncode,0);first=self.target.read_bytes()
        self.assertEqual(self.invoke('upgrade','--theme','kitty-easter','--apply').returncode,0)
        r=self.invoke('rollback','--apply');self.assertEqual(r.returncode,0,r.stderr);self.assertEqual(self.target.read_bytes(),first)
    def test_modified_upstream_refuses(self):
        (self.web/'index.lp').write_text('modified')
        r=self.invoke('install','--apply');self.assertNotEqual(r.returncode,0);self.assertIn('Unsupported',r.stderr)
        self.assertEqual(self.target.read_bytes(),b'original lcars\n')
    def test_modified_target_refuses(self):
        self.invoke('install','--apply');self.target.write_bytes(b'changed externally')
        r=self.invoke('uninstall','--apply');self.assertNotEqual(r.returncode,0)
        self.assertEqual(self.target.read_bytes(),b'changed externally')
    def test_checksum_failure_refuses(self):
        self.runner.write_text(self.runner.read_text().replace('DIGEST = ',"DIGEST = 'invalid' # ",1))
        r=self.invoke('install','--apply');self.assertNotEqual(r.returncode,0);self.assertIn('checksum',r.stderr)
        self.assertFalse(self.state.exists())
    def test_truncated_pipe_does_not_execute(self):
        partial=self.runner.read_text().split('GALACTIC_PYTHON\n}')[0]
        r=subprocess.run(['sh','-s','--','install','--apply','--web-root',str(self.web),'--state-dir',str(self.state)],input=partial,text=True,capture_output=True)
        self.assertNotEqual(r.returncode,0);self.assertFalse(self.state.exists())
    def test_invalid_action_refuses(self):
        r=self.invoke('delete-everything','--apply');self.assertNotEqual(r.returncode,0);self.assertFalse(self.state.exists())

if __name__=='__main__':unittest.main()
