#!/usr/bin/env bash
set -euo pipefail

# DarkSearch CLI bootstrap script for Linux / Termux
# - Verifies Python and pip
# - Installs Tor when possible
# - Installs Python dependency: requests[socks]
# - Prints next steps

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

SCRIPT_PYTHON=""
TOR_BIN=""

print_banner() {
  printf "\n"
  printf "\033[1;36m===============================================\033[0m\n"
  printf "\033[1;36m   DARKSEARCH CLI :: PRIVATE RESEARCH STACK   \033[0m\n"
  printf "\033[1;36m===============================================\033[0m\n"
  printf "\033[1;33m                 by R.dinesh                  \033[0m\n"
  printf "\n"
}

print_info() {
  printf "\033[1;36m[INFO]\033[0m %s\n" "$1"
}

print_warn() {
  printf "\033[1;33m[WARN]\033[0m %s\n" "$1"
}

print_err() {
  printf "\033[1;31m[ERROR]\033[0m %s\n" "$1"
}

have_cmd() {
  command -v "$1" >/dev/null 2>&1
}

resolve_tor_bin() {
  if have_cmd tor; then
    TOR_BIN="$(command -v tor)"
    return 0
  fi

  if [ -x "/usr/bin/tor" ]; then
    TOR_BIN="/usr/bin/tor"
    return 0
  fi

  if [ -x "/usr/sbin/tor" ]; then
    TOR_BIN="/usr/sbin/tor"
    return 0
  fi

  TOR_BIN=""
  return 1
}

run_privileged() {
  if [ "${EUID:-$(id -u)}" -eq 0 ]; then
    "$@"
    return
  fi

  if have_cmd sudo; then
    sudo "$@"
    return
  fi

  print_err "Root privileges are required for: $*"
  print_err "Re-run this script as root or install sudo."
  exit 1
}

is_termux() {
  [ -n "${TERMUX_VERSION:-}" ] || [ -n "${PREFIX:-}" ] && [ -d "/data/data/com.termux/files/usr" ]
}

is_tor_port_open() {
  if [ -z "$SCRIPT_PYTHON" ]; then
    return 1
  fi

  "$SCRIPT_PYTHON" - <<'PY' >/dev/null 2>&1
import socket
sock = socket.socket()
sock.settimeout(1.0)
try:
    sock.connect(("127.0.0.1", 9050))
except OSError:
    raise SystemExit(1)
finally:
    sock.close()
PY
}

wait_for_tor() {
  local retries=20
  local i=1
  while [ "$i" -le "$retries" ]; do
    if is_tor_port_open; then
      return 0
    fi
    sleep 1
    i=$((i + 1))
  done
  return 1
}

install_python_by_pkg_manager() {
  # Tries common package managers. Returns 0 on success, 1 otherwise.
  if have_cmd pkg; then
    print_info "Detected Termux (pkg). Installing Python..."
    pkg update -y
    pkg install -y python
    return 0
  fi

  if have_cmd apt-get; then
    print_info "Detected apt-get. Installing Python and pip..."
    run_privileged apt-get update
    run_privileged apt-get install -y python3 python3-pip
    return 0
  fi

  if have_cmd dnf; then
    print_info "Detected dnf. Installing Python and pip..."
    run_privileged dnf install -y python3 python3-pip
    return 0
  fi

  if have_cmd yum; then
    print_info "Detected yum. Installing Python and pip..."
    run_privileged yum install -y python3 python3-pip
    return 0
  fi

  if have_cmd pacman; then
    print_info "Detected pacman. Installing Python and pip..."
    run_privileged pacman -Sy --noconfirm python python-pip
    return 0
  fi

  if have_cmd zypper; then
    print_info "Detected zypper. Installing Python and pip..."
    run_privileged zypper install -y python3 python3-pip
    return 0
  fi

  if have_cmd apk; then
    print_info "Detected apk. Installing Python and pip..."
    run_privileged apk add --no-cache python3 py3-pip
    return 0
  fi

  return 1
}

install_tor_by_pkg_manager() {
  # Tries common package managers. Returns 0 on success, 1 otherwise.
  if have_cmd pkg; then
    print_info "Installing Tor via pkg..."
    pkg install -y tor
    resolve_tor_bin && return 0
    return 1
  fi

  if have_cmd apt-get; then
    print_info "Installing Tor via apt-get..."
    run_privileged apt-get update
    run_privileged apt-get install -y tor tor-geoipdb || run_privileged apt-get install -y tor
    resolve_tor_bin && return 0
    run_privileged apt-get install -y tor-daemon || true
    resolve_tor_bin && return 0
    return 1
  fi

  if have_cmd dnf; then
    print_info "Installing Tor via dnf..."
    run_privileged dnf install -y tor
    resolve_tor_bin && return 0
    return 1
  fi

  if have_cmd yum; then
    print_info "Installing Tor via yum..."
    run_privileged yum install -y tor
    resolve_tor_bin && return 0
    return 1
  fi

  if have_cmd pacman; then
    print_info "Installing Tor via pacman..."
    run_privileged pacman -Sy --noconfirm tor
    resolve_tor_bin && return 0
    return 1
  fi

  if have_cmd zypper; then
    print_info "Installing Tor via zypper..."
    run_privileged zypper install -y tor
    resolve_tor_bin && return 0
    return 1
  fi

  if have_cmd apk; then
    print_info "Installing Tor via apk..."
    run_privileged apk add --no-cache tor
    resolve_tor_bin && return 0
    return 1
  fi

  return 1
}

enable_tor_service_if_possible() {
  if have_cmd systemctl; then
    run_privileged systemctl enable tor >/dev/null 2>&1 || true
    run_privileged systemctl enable tor@default >/dev/null 2>&1 || true
  fi
}

start_tor_automatically() {
  if ! resolve_tor_bin; then
    return 1
  fi

  if is_tor_port_open; then
    print_info "Tor is already running on 127.0.0.1:9050"
    return 0
  fi

  if is_termux; then
    print_info "Termux detected. Starting Tor in background..."
    nohup "$TOR_BIN" >/dev/null 2>&1 &
  elif have_cmd systemctl; then
    enable_tor_service_if_possible
    print_info "Starting Tor service via systemctl..."
    run_privileged systemctl start tor || true
    run_privileged systemctl start tor@default || true
  elif have_cmd service; then
    print_info "Starting Tor service via service command..."
    run_privileged service tor start || true
  else
    print_info "Starting Tor process in background..."
    nohup "$TOR_BIN" >/dev/null 2>&1 &
  fi

  if wait_for_tor; then
    print_info "Tor started and is reachable at 127.0.0.1:9050"
    return 0
  fi

  print_warn "Tor start was attempted but port 9050 is still unreachable."
  return 1
}

print_banner
print_info "Starting DarkSearch CLI setup in: $PROJECT_DIR"

if have_cmd python3; then
  PYTHON_BIN="python3"
elif have_cmd python; then
  PYTHON_BIN="python"
else
  print_warn "Python is not installed. Attempting automatic installation..."
  if ! install_python_by_pkg_manager; then
    print_err "Could not auto-install Python (unsupported package manager)."
    print_err "Install Python 3 manually, then run this script again."
    exit 1
  fi

  if have_cmd python3; then
    PYTHON_BIN="python3"
  elif have_cmd python; then
    PYTHON_BIN="python"
  else
    print_err "Python installation attempt completed, but Python is still unavailable."
    exit 1
  fi
fi

SCRIPT_PYTHON="$PYTHON_BIN"

print_info "Using Python: $($PYTHON_BIN --version 2>&1)"

if "$PYTHON_BIN" -m pip --version >/dev/null 2>&1; then
  print_info "pip is available."
else
  print_warn "pip is not available. Attempting to bootstrap pip..."
  if ! "$PYTHON_BIN" -m ensurepip --upgrade >/dev/null 2>&1; then
    print_warn "ensurepip did not succeed. Trying package manager install for pip..."
    install_python_by_pkg_manager || true
  fi
fi

if ! "$PYTHON_BIN" -m pip --version >/dev/null 2>&1; then
  print_err "pip is still unavailable. Please install pip manually and retry."
  exit 1
fi

print_info "Upgrading pip tooling..."
"$PYTHON_BIN" -m pip install --disable-pip-version-check --upgrade pip setuptools wheel

print_info "Installing Python dependency: requests[socks]"
"$PYTHON_BIN" -m pip install --disable-pip-version-check "requests[socks]"

if resolve_tor_bin; then
  print_info "Tor command found."
else
  print_warn "Tor is not installed. Attempting automatic installation..."
  if ! install_tor_by_pkg_manager; then
    print_warn "Could not auto-install Tor (unsupported package manager)."
    print_warn "Install Tor manually to use DarkSearch CLI securely."
  fi
fi

if resolve_tor_bin; then
  print_info "Tor installation check: OK"
  if start_tor_automatically; then
    print_info "Launching DarkSearch CLI..."
    "$PYTHON_BIN" main.py
  else
    cat <<'EOF'

Tor is installed but not currently reachable on 127.0.0.1:9050.
Start Tor manually, then run:
  python3 main.py
EOF
  fi
else
  cat <<'EOF'

Setup completed with warnings.
Python dependencies are installed, but Tor is missing.
Install/start Tor, then run:
  python3 main.py
EOF
fi

print_info "Setup script completed."
