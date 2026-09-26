"""Dependency-free deterministic CSS bundle builder."""
from pathlib import Path
import argparse
import re
from urllib.parse import quote
ROOT = Path(__file__).resolve().parents[1]
THEMES = {'kitty-christmas': 'light', 'kitty-easter': 'light', 'kitty-beach-summer': 'light', 'kitty-halloween-fall': 'dark'}
def artwork(css):
    def inline(match):
        source = (ROOT / f"src/artwork/{match[1]}.svg").read_text().strip()
        return 'url("data:image/svg+xml,' + quote(source, safe="") + '")'
    return re.sub(r"@artwork\(([a-z-]+)\)", inline, css)

def build(check=False):
    for name, base in THEMES.items():
        css = ('/* Meow Kitteh. Interface code MIT; character artwork excluded: ARTWORK-NOTICE.md */\n'
               f'@import url("default-{base}.css");\n' +
               (ROOT / f"src/themes/{name}.css").read_text() +
               (ROOT / "src/dashboard.css").read_text() +
               (ROOT / "src/seasons.css").read_text())
        css = artwork(css)
        target = ROOT / f"dist/{name}.css"
        if check:
            assert target.read_text() == css, f"Stale bundle: {target}"
        else:
            target.write_text(css)
if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--check", action="store_true")
    build(p.parse_args().check)
