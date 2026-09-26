#!/usr/bin/env python3
"""Generate a local upstream-markup fixture, then serve only on loopback."""
import argparse
import functools
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import re
import shutil
from theme import check_upstream
ROOT = Path(__file__).resolve().parents[1]
def generate(upstream):
    check_upstream(upstream)
    out = ROOT / '.preview-render'; out.mkdir(exist_ok=True)
    for directory in ('vendor', 'style'):
        shutil.copytree(upstream / directory, out / directory, dirs_exist_ok=True)
    shutil.copy(upstream / 'LICENSE', out / 'UPSTREAM-LICENSE')
    for css in (ROOT / 'dist').glob('*.css'): shutil.copy(css, out / 'style/themes' / css.name)
    body = (upstream / 'index.lp').read_text().replace('<?=tablelayout?>', 'col-md-6')
    body = re.sub(r'<\?.*?\?>', '', body, flags=re.S)
    body = re.sub(r'<script.*?</script>', '', body, flags=re.S)
    template = (ROOT / 'preview/shell.html').read_text()
    (out / 'index.html').write_text(template.replace('<!-- DASHBOARD -->', body))
    shutil.copy(ROOT / 'preview/demo.js', out / 'demo.js')
    return out
if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--upstream', required=True, type=Path)
    p.add_argument('--port', default=8766, type=int);p.add_argument('--generate-only', action='store_true')
    a=p.parse_args();out=generate(a.upstream.resolve())
    if not a.generate_only:
        print(f'Fixture only, synthetic data: http://127.0.0.1:{a.port}', flush=True)
        ThreadingHTTPServer(('127.0.0.1',a.port),functools.partial(SimpleHTTPRequestHandler,directory=str(out))).serve_forever()
