#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
    echo "[!] Run as root: sudo ./uninstall.sh"
    exit 1
fi

systemctl stop tor 2>/dev/null || true

rm -f /usr/local/bin/rsip
rm -rf /opt/rsip
rm -rf /etc/rsip

echo "[+] RsiP files removed."
echo "[!] Tor itself was left installed."
echo "    If you no longer need Tor: sudo apt remove tor"
