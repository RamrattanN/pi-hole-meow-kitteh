# Docker testing plan

No container has been launched and no production ports or volumes have been touched. Docker is unavailable in this environment.

For an approved disposable test only, choose an official Pi-hole image by immutable digest, verify its installed Web files against `upstream-lock.json`, and record its Core/FTL/Web versions. Do not assume a Docker date tag corresponds to Web v6.6.

Use a read-only **single-file bind mount** of the desired `dist/*.css` onto `/var/www/html/admin/style/themes/lcars.css` (adjust only after inspecting the chosen image). The default-light/default-dark imports remain inside the image. Do not mount over the whole themes folder. Select `FTLCONF_webserver_interface_theme: 'lcars'` in that test container. An environment setting may override UI configuration; remove it on rollback.

Create a disposable Compose project with a new empty configuration volume, a loopback-only HTTP mapping such as `127.0.0.1:8088:80`, and no published port 53, host network, DHCP capability, production DNS routing, privileged mode or live Pi-hole volumes. Keep ordinary Pi-hole authentication enabled and configure any test secret yourself; none is embedded here. The image and credentials are deliberately not guessed, so this is a plan rather than a runnable Compose file.

The host installer uses atomic file replacement and is not designed to mutate a bind-mounted file from inside the container. Switch bundles on the host and recreate the disposable container to avoid stale bind-mount inodes. Roll back by removing the file mount and theme environment override, then recreate from the same pinned image. Verify that the image's original stylesheet is restored. Preserve test logs without secrets.

Official references: [Docker configuration](https://docs.pi-hole.net/docker/configuration/) and [FTL theme settings](https://docs.pi-hole.net/ftldns/configfile/#theme).
