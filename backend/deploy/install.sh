#!/usr/bin/env bash
# Install script per astroarch-bridge su AstroArch / ArchLinux / Debian.
#
# Uso:
#   sudo bash install.sh           (installazione standard)
#   sudo bash install.sh --user $(whoami)  (per usare il proprio utente invece di "astroarch")
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

TARGET_USER="astroarch"
INSTALL_PIP=1

while [[ $# -gt 0 ]]; do
  case "$1" in
    --user) TARGET_USER="$2"; shift 2;;
    --no-pip) INSTALL_PIP=0; shift;;
    *) echo "unknown arg: $1"; exit 1;;
  esac
done

if [[ $EUID -ne 0 ]]; then
  echo "must be run as root (use sudo)"; exit 1
fi

echo "==> astroarch-bridge install (user: $TARGET_USER)"

# 1. utente
if ! id -u "$TARGET_USER" >/dev/null 2>&1; then
  echo "==> creating user $TARGET_USER"
  useradd -m -s /bin/bash "$TARGET_USER"
fi

# 2. python
if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not installed - install it via your package manager"; exit 1
fi

# 3. pip install
if [[ $INSTALL_PIP -eq 1 ]]; then
  echo "==> installing python deps system-wide"
  python3 -m pip install --break-system-packages --upgrade pip || true
  python3 -m pip install --break-system-packages -r "$BACKEND_DIR/requirements.txt"
  python3 -m pip install --break-system-packages "$BACKEND_DIR"
fi

# 4. cartelle
HOME_DIR="$(getent passwd "$TARGET_USER" | cut -d: -f6)"
mkdir -p "$HOME_DIR/.config/astroarch-bridge"
mkdir -p "$HOME_DIR/Pictures/Ekos"
chown -R "$TARGET_USER":"$TARGET_USER" "$HOME_DIR/.config/astroarch-bridge" "$HOME_DIR/Pictures/Ekos"
chmod 700 "$HOME_DIR/.config/astroarch-bridge"

# 5. systemd unit
SERVICE_SRC="$SCRIPT_DIR/astroarch-bridge.service"
SERVICE_DST="/etc/systemd/system/astroarch-bridge.service"
cp "$SERVICE_SRC" "$SERVICE_DST"
sed -i "s|^User=.*|User=$TARGET_USER|" "$SERVICE_DST"
sed -i "s|^Group=.*|Group=$TARGET_USER|" "$SERVICE_DST"
sed -i "s|/home/astroarch/|$HOME_DIR/|g" "$SERVICE_DST"

systemctl daemon-reload
systemctl enable astroarch-bridge.service
systemctl restart astroarch-bridge.service

# 6. mostra token
sleep 1
TOKEN_FILE="$HOME_DIR/.config/astroarch-bridge/token"
if [[ -f "$TOKEN_FILE" ]]; then
  echo
  echo "==> astroarch-bridge installed and running"
  echo "    URL:   http://$(hostname -I | awk '{print $1}'):8765"
  echo "    Token: $(cat "$TOKEN_FILE")"
  echo
  echo "    Status: systemctl status astroarch-bridge"
  echo "    Logs:   journalctl -u astroarch-bridge -f"
else
  echo "==> installed but token file not yet created (service may still be starting)"
fi
