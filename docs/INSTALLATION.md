# Installation, update and recovery

For installation without a Git checkout, see the [curl runner guide](CURL-RUNNER.md). The runner invokes the same transaction engine and journal format described here.

**Development procedure only. Obtain approval and use an isolated Pi-hole v6 test instance. Do not run on Nilesh's live Pi-hole.** Python 3.9+ and ordinary Unix file permissions are required. Inspect the source and run tests first. The target must match the inspected v6.6 files; paths cannot contain symlinks. A pre-existing custom LCARS stylesheet will be backed up exactly.

Example paths below are placeholders for an approved test machine. The restore directory must be private, outside the entire HTTP-served tree, and retained across updates. The script can only verify that it is outside `--web-root`; the operator must ensure it is also outside other served directories.

```sh
# Read-only plan; no files are created.
./install.sh --web-root /path/to/test/admin --state-dir /path/to/private/kitty-state --theme kitty-christmas
# After approval, append --apply to that same command.
```

The scripts deliberately do not change FTL settings. Record the current theme setting separately, then select **Star Trek LCARS** in the approved test instance's web-interface settings. The light variant uses the same slot. Hard-refresh after switching CSS. Existing upstream browser theme metadata and bundled LCARS font loading remain unchanged.

```sh
./update.sh --web-root /path/to/test/admin --state-dir /path/to/private/kitty-state --theme kitty-easter
./rollback.sh --web-root /path/to/test/admin --state-dir /path/to/private/kitty-state
./uninstall.sh --web-root /path/to/test/admin --state-dir /path/to/private/kitty-state
./recover.sh --web-root /path/to/test/admin --state-dir /path/to/private/kitty-state
```

Each is a dry-run until `--apply` is appended. `update` uses reviewed local bundles; it never downloads or executes a remote installer. `rollback` returns one committed step (the first rollback after a single install restores the original). `uninstall` returns directly to the original LCARS file. Restore your separately recorded FTL setting manually if you changed it. No credentials, databases or Pi-hole configuration are read by these scripts.

If a write is interrupted, other mutations refuse until `recover` runs. Recovery restores the last committed file, then clears the pending transaction. If an unrelated process has changed the CSS, preserve the new file and journal and investigate; there is deliberately no force flag. Do not overwrite a Pi-hole upgrade with an old backup. The journal is retained after uninstall so that recovery and audit evidence remain available. Do not remove it while the theme is installed.

Before upgrading Pi-hole, uninstall and restore the prior FTL theme setting. After upgrading, reassess the new upstream source and create a new private state directory so the baseline belongs to that version. No `git reset --hard`, broad directory replacement or automatic service control is used.
