# Security

This prototype has no API client and collects no credentials. Do not include passwords, tokens, production hostnames or personal DNS logs in issues. For a suspected security defect, report privately to the repository owner through an available private GitHub channel after the repository is created. Until one exists, do not publish sensitive details in a public issue.

The installer is a local file tool, not a privilege boundary. Use a trusted checkout and a private restore directory, avoid concurrent upstream updates, and inspect release changes before running them. The downloadable runner is generated from reviewed repository files and contains its own payload. It performs no subsequent network requests or automatic self-updates. Inspect and pin downloaded code before applying; its embedded checksum is not a cryptographic signature.
