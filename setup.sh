#!/usr/bin/env bash
set -euo pipefail

# ===============================================
# DARKSEARCH CLI :: PRIVATE RESEARCH STACK
# ===============================================
# One-command installer and launcher for:
# - Kali Linux / Ubuntu / Debian
# - Termux
# ===============================================

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

ENV_TYPE="unknown"
PYTHON_BIN=""

print_banner() {
  printf "\n"
  printf "===============================================\n"
  printf "DARKSEARCH CLI :: PRIVATE RESEARCH STACK\n"
  printf "===============================================\n"
  printf "             by R.dinesh\n"
  printf "\n"
}

print_info() {
  printf "[INFO] %s\n" "$1"
}

print_ok() {
  printf "[OK] %s\n" "$1"
}

print_error() {
  printf "[ERROR] %s\n" "$1" >&2
}

on_error() {
  print_error "Something went wrong during setup."
  exit 1
}
trap on_error ERR

have_cmd() {
  command -v "$1" >/dev/null 2>&1
}

run_as_root_if_needed() {
  if [ "${EUID:-$(id -u)}" -eq 0 ]; then
    "$@"
    return
  fi

  if have_cmd sudo; then
    sudo "$@"
    return
  fi

  print_error "This step requires root privileges: $*"
  print_error "Run as root or install sudo."
  exit 1
}

check_internet() {
  print_info "Checking internet connectivity..."

  if have_cmd curl; then
    if curl -s --max-time 8 https://check.torproject.org >/dev/null; then
      print_ok "Internet connectivity detected."
      return
    fi
  fi

  if have_cmd wget; then
    if wget -q --spider --timeout=8 https://check.torproject.org; then
      print_ok "Internet connectivity detected."
      return
    fi
  fi

  if ping -c 1 -W 2 1.1.1.1 >/dev/null 2>&1; then
    print_ok "Internet connectivity detected."
    return
  fi

  print_error "No internet connectivity. Please connect and retry."
  exit 1
}

detect_environment() {
  print_info "Detecting environment..."

  if [ -n "${TERMUX_VERSION:-}" ] || [ -d "/data/data/com.termux/files/usr" ]; then
    ENV_TYPE="termux"
    print_ok "Environment detected: Termux"
    return
  fi

  if have_cmd apt-get || have_cmd apt; then
    ENV_TYPE="debian"
    print_ok "Environment detected: Debian/Kali/Ubuntu"
    return
  fi

  print_error "Unsupported environment. This installer supports Termux and Debian-based Linux."
  exit 1
}

resolve_python() {
  if have_cmd python3; then
    PYTHON_BIN="python3"
  elif have_cmd python; then
    PYTHON_BIN="python"
  else
    PYTHON_BIN=""
  fi
}

install_dependencies_termux() {
  print_info "Installing dependencies using pkg..."

  if ! have_cmd python3 && ! have_cmd python; then
    pkg update -y
    pkg install -y python
  else
    print_info "Python already installed. Skipping Python install."
  fi

  if ! have_cmd pip && ! have_cmd pip3; then
    pkg install -y python-pip || true
  else
    print_info "pip already installed. Skipping pip install."
  fi

  if ! have_cmd tor; then
    pkg install -y tor
  else
    print_info "Tor already installed. Skipping Tor install."
  fi

  print_ok "Dependency installation finished (Termux)."
}

install_dependencies_debian() {
  print_info "Installing dependencies using apt..."

  run_as_root_if_needed apt-get update

  missing=()
  have_cmd python3 || missing+=(python3)

  if ! python3 -m pip --version >/dev/null 2>&1; then
    missing+=(python3-pip)
  fi

  have_cmd tor || missing+=(tor)

  if [ "${#missing[@]}" -eq 0 ]; then
    print_info "Python3, pip, and Tor already installed."
  else
    print_info "Installing missing packages: ${missing[*]}"
    run_as_root_if_needed apt-get install -y "${missing[@]}"
  fi

  print_ok "Dependency installation finished (Debian/Kali/Ubuntu)."
}

setup_python_packages() {
  resolve_python

  if [ -z "$PYTHON_BIN" ]; then
    print_error "Python is not available after installation."
    exit 1
  fi

  print_info "Using Python: $($PYTHON_BIN --version 2>&1)"

  if ! "$PYTHON_BIN" -m pip --version >/dev/null 2>&1; then
    print_info "pip module missing. Attempting bootstrap via ensurepip..."
    "$PYTHON_BIN" -m ensurepip --upgrade || true
  fi

  if ! "$PYTHON_BIN" -m pip --version >/dev/null 2>&1; then
    print_error "pip is not available."
    exit 1
  fi

  print_info "Upgrading pip..."
  "$PYTHON_BIN" -m pip install --disable-pip-version-check --upgrade pip

  print_info "Installing Python package: requests[socks]"
  "$PYTHON_BIN" -m pip install --disable-pip-version-check "requests[socks]"

  print_ok "Python environment configured."
}

start_tor() {
  print_info "Starting Tor..."

  if pgrep -x tor >/dev/null 2>&1; then
    print_info "Tor process already running."
    return
  fi

  tor >/dev/null 2>&1 &
  disown || true

  sleep 3
}

verify_tor() {
  print_info "Validating Tor SOCKS endpoint on 127.0.0.1:9050..."

  resolve_python
  if [ -z "$PYTHON_BIN" ]; then
    print_error "Python is required for Tor validation."
    exit 1
  fi

  if "$PYTHON_BIN" - <<'PY' >/dev/null 2>&1
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
  then
    print_ok "Tor is running on 127.0.0.1:9050"
  else
    print_error "Tor is not running on 127.0.0.1:9050"
    print_error "Tor setup failed. Please check Tor installation logs."
    exit 1
  fi
}

validate_project() {
  print_info "Validating project files..."

  if [ ! -f "$PROJECT_DIR/main.py" ]; then
    print_error "Missing required file: main.py"
    exit 1
  fi

  if [ ! -d "$PROJECT_DIR/cli" ] || [ ! -d "$PROJECT_DIR/core" ] || [ ! -d "$PROJECT_DIR/engines" ] || [ ! -d "$PROJECT_DIR/processing" ] || [ ! -d "$PROJECT_DIR/privacy" ] || [ ! -d "$PROJECT_DIR/utils" ]; then
    print_error "Missing one or more required root directories: cli/, core/, engines/, processing/, privacy/, utils/"
    exit 1
  fi

  print_ok "Project validation passed."
}

set_permissions() {
  print_info "Setting executable permission on main.py..."
  chmod +x "$PROJECT_DIR/main.py"
  print_ok "Permissions updated."
}

launch_app() {
  resolve_python
  if [ -z "$PYTHON_BIN" ]; then
    print_error "Python not found. Cannot launch DarkSearch CLI."
    exit 1
  fi

  print_ok "Setup complete. Launching DarkSearch CLI..."
  "$PYTHON_BIN" "$PROJECT_DIR/main.py"
}

main() {
  print_banner
  check_internet
  detect_environment

  case "$ENV_TYPE" in
    termux)
      install_dependencies_termux
      ;;
    debian)
      install_dependencies_debian
      ;;
    *)
      print_error "Unsupported environment state."
      exit 1
      ;;
  esac

  setup_python_packages
  start_tor
  verify_tor
  validate_project
  set_permissions
  launch_app
}

main "$@"
