#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="/opt/rsip"
BIN_PATH="/usr/local/bin/rsip"
CONF_DIR="/etc/rsip"
PASSWORD_FILE="${CONF_DIR}/tor-control-password"
TORRC="/etc/tor/torrc"

if [[ "${EUID}" -ne 0 ]]; then
    echo "[!] Run this installer as root:"
    echo "    sudo ./install.sh"
    exit 1
fi

echo "[*] Installing RsiP dependencies..."

apt-get update
apt-get install -y tor python3 python3-pip python3-venv figlet

echo "[*] Creating application directory..."
rm -rf "${INSTALL_DIR}"
mkdir -p "${INSTALL_DIR}"
cp -r "${APP_DIR}/core" "${INSTALL_DIR}/"
cp "${APP_DIR}/rsip.py" "${INSTALL_DIR}/"
cp "${APP_DIR}/requirements.txt" "${INSTALL_DIR}/"

python3 -m venv "${INSTALL_DIR}/venv"
"${INSTALL_DIR}/venv/bin/pip" install --upgrade pip
"${INSTALL_DIR}/venv/bin/pip" install -r "${INSTALL_DIR}/requirements.txt"

echo "[*] Configuring Tor ControlPort..."

mkdir -p "${CONF_DIR}"

if grep -qE '^[[:space:]]*ControlPort[[:space:]]+9051' "${TORRC}" 2>/dev/null; then
    :
else
    printf '\n# RsiP\nControlPort 9051\n' >> "${TORRC}"
fi

PASSWORD="$(python3 - <<'PY'
import secrets
print(secrets.token_urlsafe(32))
PY
)"

HASHED_PASSWORD="$(tor --hash-password "${PASSWORD}" | tail -n 1)"

if grep -qE '^[[:space:]]*HashedControlPassword[[:space:]]+' "${TORRC}" 2>/dev/null; then
    sed -i "s|^[[:space:]]*HashedControlPassword.*|HashedControlPassword ${HASHED_PASSWORD}|" "${TORRC}"
else
    printf 'HashedControlPassword %s\n' "${HASHED_PASSWORD}" >> "${TORRC}"
fi

printf '%s\n' "${PASSWORD}" > "${PASSWORD_FILE}"
chmod 600 "${PASSWORD_FILE}"
chmod 755 "${INSTALL_DIR}"
chmod 755 "${INSTALL_DIR}/rsip.py"

cat > "${BIN_PATH}" <<EOF
#!/usr/bin/env bash
exec "${INSTALL_DIR}/venv/bin/python" "${INSTALL_DIR}/rsip.py" "\$@"
EOF

chmod 755 "${BIN_PATH}"

echo "[*] Restarting Tor..."
systemctl enable tor
systemctl restart tor

sleep 3

echo
echo "[+] RsiP installed successfully."
echo
echo "    Try:"
echo "      rsip status"
echo "      rsip rotate"
echo "      rsip start --interval 10"
echo
echo "[!] Note: Tor controls the public exit IP seen by sites."
echo "    Tyger! Tyger! burning bright. In the forests of the night."
