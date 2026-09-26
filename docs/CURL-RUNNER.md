# Downloadable installation runner

The runner is experimental and targets the inspected Pi-hole Web v6.6 files. Use an approved isolated test instance until runtime validation is complete. It changes theme CSS only, not DNS, credentials or FTL configuration.

## Download once, inspect, then run

Requires curl, a POSIX shell and Python 3.9+ on a Unix host. The download below tracks the experimental `develop` branch; no stable release is available yet. To pin a reviewed version, replace `develop` in the URL with its full Git commit SHA.

```sh
curl --fail --show-error --silent --location --proto '=https' --proto-redir '=https' \
  https://raw.githubusercontent.com/RamrattanN/pi-hole-meow-kitteh/develop/run.sh \
  --output meow-kitteh-runner.sh && sh meow-kitteh-runner.sh --help
```

Inspect the saved file before applying it. The readable bootstrap, embedded payload and SHA-256 self-check are generated from this repository by `scripts/build_runner.py`. The checksum detects payload corruption; it is **not a signature** or protection against a maliciously replaced runner. Pinning a reviewed Git commit prevents following later branch changes.

## Install

```sh
# Check first; neither webroot nor restore journal is changed.
sh meow-kitteh-runner.sh install --theme kitty-christmas --dry-run
# Apply on the approved test host, using sudo only if its permissions require it.
sudo sh meow-kitteh-runner.sh install --theme kitty-christmas --apply
```

Season IDs are `kitty-christmas`, `kitty-easter`, `kitty-beach-summer` and `kitty-halloween-fall`. Omitted install theme defaults to Christmas Wishes. Defaults are `/var/www/html/admin` for the webroot and `/var/lib/pi-hole-meow-kitteh` for the restore directory. Override both when needed:

```sh
sh meow-kitteh-runner.sh install --theme kitty-easter \
  --web-root /path/to/test/admin --state-dir /path/to/private/kitty-state
```

Keep the restore directory outside all HTTP-served directories. If an existing journal needs privileged read access, run the dry-run with the same privileges required to read it. No automatic elevation is attempted.

After applying, record your current Pi-hole theme selection and choose the existing **Star Trek LCARS** slot in Pi-hole's web settings, then hard-refresh. The runner prints this instruction. It does not change that selection itself.

## Upgrade or switch themes

Download the newly reviewed runner from the desired commit or branch using the first command again. Then:

```sh
sh meow-kitteh-runner.sh upgrade --dry-run
sudo sh meow-kitteh-runner.sh upgrade --apply
# Optional explicit theme switch:
sudo sh meow-kitteh-runner.sh upgrade --theme kitty-easter --apply
```

`upgrade` (also named `update`) preserves the currently installed palette unless `--theme` is provided. Running the same downloaded runner again will not fetch newer code; it applies only the version embedded in that file. `--version` shows its development version and payload identifier. An identical installed bundle is a no-op.

For installations made with the earlier checkout scripts, supply the same `--web-root` and `--state-dir` used at installation. The runner understands those existing journals and infers known palette markers; it refuses an unknown palette unless you specify it.

## Uninstall, rollback and interrupted-write recovery

The saved runner works offline and without a repository checkout:

```sh
sh meow-kitteh-runner.sh uninstall --dry-run
sudo sh meow-kitteh-runner.sh uninstall --apply
sudo sh meow-kitteh-runner.sh rollback --apply
sudo sh meow-kitteh-runner.sh recover --apply
```

Always reuse your original path overrides. Uninstall restores the original LCARS bytes. Rollback restores the previous committed stylesheet. Recovery handles interrupted transactions. The journal remains available afterward. Restore your previous Pi-hole theme setting manually if you changed it.

Unexpected upstream changes or third-party stylesheet edits cause a refusal; there is no force flag. See [installation and recovery](INSTALLATION.md). The runner is for ordinary host files, not replacement of a file bind-mounted inside a container; see [Docker guidance](DOCKER.md).

## Pipe support

The runner also accepts `curl ... | sh -s -- install ...`, but the saved-file approach above makes download failures visible before execution, permits inspection, and leaves an offline recovery tool. No arguments prints help. Every action defaults to dry-run; `--apply` is required to write. A truncated runner before its final invocation cannot start an installation.

The runner contains all four CSS bundles, the source compatibility lock and the existing transactional installer. It creates a temporary private unpack directory and removes it on normal exit. Dry-run means no target/journal mutation, not zero temporary filesystem activity. It makes no network calls once downloaded, modifies no shell profiles and installs no global command.
