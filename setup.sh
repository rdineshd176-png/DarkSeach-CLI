#!/usr/bin/env bash
set -euo pipefail

# DarkSearch CLI bootstrap script for Linux / Termux
# - Verifies Python and pip
# - Installs Tor when possible
# - Installs Python dependency: requests[socks]
# - Prints next steps

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

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
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip
    return 0
  fi

  if have_cmd dnf; then
    print_info "Detected dnf. Installing Python and pip..."
    sudo dnf install -y python3 python3-pip
    return 0
  fi

  if have_cmd yum; then
    print_info "Detected yum. Installing Python and pip..."
    sudo yum install -y python3 python3-pip
    return 0
  fi

  if have_cmd pacman; then
    print_info "Detected pacman. Installing Python and pip..."
    sudo pacman -Sy --noconfirm python python-pip
    return 0
  fi

  if have_cmd zypper; then
    print_info "Detected zypper. Installing Python and pip..."
    sudo zypper install -y python3 python3-pip
    return 0
  fi

  if have_cmd apk; then
    print_info "Detected apk. Installing Python and pip..."
    sudo apk add --no-cache python3 py3-pip
    return 0
  fi

  return 1
}

install_tor_by_pkg_manager() {
  # Tries common package managers. Returns 0 on success, 1 otherwise.
  if have_cmd pkg; then
    print_info "Installing Tor via pkg..."
    pkg install -y tor
    return 0
  fi

  if have_cmd apt-get; then
    print_info "Installing Tor via apt-get..."
    sudo apt-get update
    sudo apt-get install -y tor
    return 0
  fi

  if have_cmd dnf; then
    print_info "Installing Tor via dnf..."
    sudo dnf install -y tor
    return 0
  fi

  if have_cmd yum; then
    print_info "Installing Tor via yum..."
    sudo yum install -y tor
    return 0
  fi

  if have_cmd pacman; then
    print_info "Installing Tor via pacman..."
    sudo pacman -Sy --noconfirm tor
    return 0
  fi

  if have_cmd zypper; then
    print_info "Installing Tor via zypper..."
    sudo zypper install -y tor
    return 0
  fi

  if have_cmd apk; then
    print_info "Installing Tor via apk..."
    sudo apk add --no-cache tor
    return 0
  fi

  return 1
}

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
"$PYTHON_BIN" -m pip install --upgrade pip setuptools wheel

print_info "Installing Python dependency: requests[socks]"
"$PYTHON_BIN" -m pip install "requests[socks]"

if have_cmd tor; then
  print_info "Tor command found."
else
  print_warn "Tor is not installed. Attempting automatic installation..."
  if ! install_tor_by_pkg_manager; then
    print_warn "Could not auto-install Tor (unsupported package manager)."
    print_warn "Install Tor manually to use DarkSearch CLI securely."
  fi
fi

if have_cmd tor; then
  print_info "Tor installation check: OK"
  cat <<'EOF'

Next steps:
1) Start Tor:
   - tor
   - or service tor start
2) Run DarkSearch CLI:
   python3 main.py
   (or: python main.py)
EOF
else
  cat <<'EOF'

Setup completed with warnings.
Python dependencies are installed, but Tor is missing.
Install/start Tor, then run:
  python3 main.py
EOF
fi

print_info "Setup script completed."
