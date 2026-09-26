# Development workflow

The local repository has `main` as the stable starting point and `develop` for the prototype. Work in short feature branches from `develop`; open pull requests into `develop`. Promote a reviewed, tested release through a pull request into `main`, then tag it. `main` is not a claim that the initial scaffold is a production-ready release.

Nilesh approved public repository creation on 2026-09-26. The repository is https://github.com/RamrattanN/pi-hole-meow-kitteh. Development remains on `develop`, with releases promoted to `main` only after review and isolated runtime validation. No live Pi-hole credentials or configuration have been accessed.

GitHub `main` protection enabled and verified on 2026-09-26: pull requests required, `verify` required with an up-to-date branch, conversations must be resolved, administrator enforcement enabled, force-pushes and deletion disabled. Required approving reviews are zero for the solo-maintainer workflow; this still requires a pull request and passing checks. `develop` holds experimental work. Release only reviewed main commits.

```sh
python3 scripts/build.py
python3 scripts/build_runner.py
python3 scripts/build.py --check
python3 scripts/build_runner.py --check
sh -n run.sh
python3 -m unittest discover -s tests -v
node --check preview/demo.js
```

CI performs those checks. For upstream updates, inspect the pinned files, update lock hashes only after review, render both themes, run the isolated runtime checklist, and revise the matrix. Never merely refresh hashes to bypass a refusal. CSS bundles must remain deterministic, self-contained except for their documented upstream base import, and free of network dependencies.

Do not commit generated upstream trees, local journals, secrets, logs from live systems or production configuration. Discuss upstream source reuse and license obligations before including any third-party code/assets. Review screenshots for private data before publication.

Regenerate `run.sh` after changes to the installer, theme bundles, compatibility lock, version or license. CI rejects a stale runner. Its embedded checksum is an integrity check, not a signing mechanism.
