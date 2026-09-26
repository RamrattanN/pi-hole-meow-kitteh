#!/usr/bin/env python3
"""Transactional, single-file theme management. Never invokes Pi-hole or Git."""
import argparse
import base64
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile

ROOT = Path(__file__).resolve().parents[1]
THEMES = ('kitty-christmas', 'kitty-easter', 'kitty-beach-summer', 'kitty-halloween-fall')
def digest(data):
    return hashlib.sha256(data).hexdigest()
def pack(data):
    return {'sha256': digest(data), 'data': base64.b64encode(data).decode()}
def unpack(record):
    data = base64.b64decode(record['data'], validate=True)
    if digest(data) != record['sha256']:
        raise ValueError('Corrupt restore journal')
    return data

def regular(path):
    # Reject symlinks in every component, including the target itself.
    for part in [path, *path.parents]:
        if part.is_symlink():
            raise ValueError(f'Symlinks are not supported: {part}')
    if not path.is_file():
        raise ValueError(f'Expected a regular file: {path}')

def atomic(path, data, mode=0o600, owner=None):
    fd, temp = tempfile.mkstemp(prefix='.meow-kitteh-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as out:
            out.write(data); out.flush(); os.fchmod(out.fileno(), mode)
            if owner is not None and hasattr(os, 'fchown'):
                current = os.fstat(out.fileno())
                if (current.st_uid, current.st_gid) != tuple(owner):
                    os.fchown(out.fileno(), *owner)
            os.fsync(out.fileno())
        os.replace(temp, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try: os.fsync(directory)
        finally: os.close(directory)
    finally:
        if os.path.exists(temp): os.unlink(temp)

def save(path, state):
    atomic(path, (json.dumps(state, indent=2)+'\n').encode())

@contextmanager
def locked(state_dir):
    import fcntl
    state_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    lock = state_dir / 'lock'
    if lock.is_symlink(): raise ValueError('Lock is a symlink')
    with lock.open('a') as handle:
        try: fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError: raise ValueError('Another theme operation is running')
        yield

def check_upstream(web):
    lock = json.loads((ROOT / 'docs/upstream-lock.json').read_text())
    for name, expected in lock['files'].items():
        path = web / name; regular(path)
        if digest(path.read_bytes()) != expected:
            raise ValueError(f'Unsupported or changed upstream file: {name}. Reassess compatibility first.')

def run(action, web, state_dir, theme=None, apply=False):
    web = Path(os.path.abspath(web)); state_dir = Path(os.path.abspath(state_dir))
    for path in [web, state_dir]:
        for part in [path, *path.parents]:
            if part.is_symlink(): raise ValueError('Symlink paths are not supported')
    if state_dir == web or web in state_dir.parents:
        raise ValueError('Restore journal must be outside the served web root')
    target = web / 'style/themes/lcars.css'; regular(target)
    journal = state_dir / 'state.json'
    if journal.is_symlink(): raise ValueError('Journal is a symlink')
    # Dry runs do not create state directories or lock files.
    if apply:
        with locked(state_dir):
            return perform(action, web, target, journal, theme, True)
    return perform(action, web, target, journal, theme, False)

def perform(action, web, target, journal, theme, apply):
    current = target.read_bytes()
    state = json.loads(journal.read_text()) if journal.exists() else None
    if state:
        if state.get('schema') != 1 or state['target'] != str(target):
            raise ValueError('Journal does not belong to this target')
        for record in state['history']: unpack(record)
        if state.get('pending'):
            pending = state['pending']; unpack(pending)
            if action != 'recover':
                raise ValueError('Interrupted transaction: run recover first')
            if digest(current) not in (pending['sha256'], state['history'][-1]['sha256']):
                raise ValueError('Target changed outside the installer; preserve and investigate it')
            desired = unpack(state['history'][-1])
            if apply:
                atomic(target, desired, state['mode'], state['owner'])
                state.pop('pending'); save(journal, state)
            return 'Recovered last committed theme' if apply else 'Would recover last committed theme'
        if digest(current) != state['history'][-1]['sha256']:
            raise ValueError('Target changed outside the installer; refusing to overwrite it')
    elif action != 'install':
        raise ValueError('No restore journal; install first')
    if action == 'recover': return 'No interrupted transaction'
    if action in ('install', 'update'):
        if theme not in THEMES: raise ValueError('Choose a supported --theme')
        if action == 'install' and state and len(state['history']) > 1:
            raise ValueError('Already installed; use update')
        if action == 'update' and len(state['history']) < 2:
            raise ValueError('Theme is uninstalled; use install')
        check_upstream(web)
        desired = (ROOT / f'dist/{theme}.css').read_bytes()
        if state is None:
            info = target.stat()
            state = {'schema':1, 'target':str(target), 'mode':stat.S_IMODE(info.st_mode),
                     'owner':[info.st_uid,info.st_gid], 'history':[pack(current)]}
        history = state['history'] + [pack(desired)]
        if current == desired: return 'Theme already matches; no changes'
    elif action == 'rollback':
        if len(state['history']) < 2: raise ValueError('Nothing to roll back')
        history = state['history'][:-1]; desired = unpack(history[-1])
    elif action == 'uninstall':
        history = state['history'][:1]; desired = unpack(history[0])
    else:
        raise ValueError('Unknown action')
    if apply:
        # Persist both possible target hashes BEFORE atomic file replacement.
        state['pending'] = pack(desired); save(journal, state)
        atomic(target, desired, state['mode'], state['owner'])
        state['history'] = history; state.pop('pending'); save(journal, state)
    return f"{'Applied' if apply else 'Would apply'} {action}: {target}"

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=('install','update','rollback','uninstall','recover'))
    p.add_argument('--web-root', required=True, help='Explicit Pi-hole admin directory')
    p.add_argument('--state-dir', required=True, help='Private restore directory outside web root')
    p.add_argument('--theme', choices=THEMES)
    p.add_argument('--apply', action='store_true', help='Write changes; default is read-only dry run')
    a = p.parse_args()
    try: print(run(a.action, a.web_root, a.state_dir, a.theme, a.apply))
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        p.exit(1, f'Refused: {exc}\n')
