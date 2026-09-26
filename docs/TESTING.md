# Validation

The inherited installer and standalone-runner tests execute against disposable files, not a live Pi-hole. The seasonal suite additionally exercises installation, theme-preserving upgrade and byte-exact uninstall for each of the four season IDs.

Build checks verify deterministic CSS and runner generation. Original SVG files are parsed to verify valid XML and absence of scripts or external references. Browser fixture inspection covers all four palettes, chart rendering, desktop and mobile widths. Screenshots contain synthetic data only.

Pending: actual authentication, API polling, chart interactions, blocking controls, CSS data-URL policy, login/base-theme fallback pages, Firefox/Safari, assistive-technology audit and actual target filesystem/container installation. Do not infer runtime compatibility from fixture tests.

## Local results — 2026-09-26

All 24 tests passed, including a four-season runner round trip. CSS/runner generation and JavaScript/shell syntax checks passed. All four SVG illustrations parsed without scripts or external references. Desktop previews were inspected at 1440×1000 and mobile previews at 390×844. Document widths were 1425 and 375 respectively (scrollbars accounted for); no horizontal overflow. Four-season switching and populated synthetic charts were checked. No live Pi-hole was accessed.
