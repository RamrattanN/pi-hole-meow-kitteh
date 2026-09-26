# Compatibility

The dashboard integration reuses the inspected Pi-hole Web v6.6 mechanism: `header.lp` loads a named CSS file and the authenticated body exposes page classes. The runner replaces `style/themes/lcars.css`, importing the installed default-light theme for Christmas, Easter and Summer, or default-dark for Halloween. The seven exact integration-file hashes are recorded in `upstream-lock.json`.

Source: https://github.com/pi-hole/web/tree/b2a4078446519c58d84f199663ca9326d5d311f0

FTL's documented `webserver.interface.theme` setting includes the LCARS slot. Arbitrary new theme names are not added to FTL. The runner never changes that setting. https://docs.pi-hole.net/ftldns/configfile/#theme

Original SVG artwork is embedded as CSS data URLs. It introduces no external image/font requests and no deployed JavaScript. Test the target installation's content-security policy and actual browser behavior before a release. Mobile, boxed and normal layouts need both fixture checks and an isolated runtime smoke test.

Earlier/newer Web versions are refused when their file hashes differ. Pi-hole v5 is unsupported. Non-dashboard pages inherit the upstream base styling and have not been redesigned. No actual FTL process, DNS resolution, API polling or Docker image has been tested for this collection. Docker guidance is a plan only.
