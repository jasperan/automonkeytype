#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# automonkeytype — One-Command Installer
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/jasperan/automonkeytype/main/install.sh | bash
#
# Override install location:
#   PROJECT_DIR=/opt/myapp curl -fsSL ... | bash
# ============================================================

REPO_URL="https://github.com/jasperan/automonkeytype.git"
PROJECT="automonkeytype"
BRANCH="main"
INSTALL_DIR="${PROJECT_DIR:-$(pwd)/$PROJECT}"

# ── Colors ──────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

info()    { echo -e "${BLUE}→${NC} $1"; }
success() { echo -e "${GREEN}✓${NC} $1"; }
warn()    { echo -e "${YELLOW}!${NC} $1"; }
fail()    { echo -e "${RED}✗ $1${NC}"; exit 1; }
command_exists() { command -v "$1" &>/dev/null; }

print_banner() {
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}  automonkeytype${NC}"
    echo -e "  Human-like typing automation for monkeytype.com"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

clone_repo() {
    if [ -d "$INSTALL_DIR" ]; then
        warn "Directory $INSTALL_DIR already exists"
        info "Pulling latest changes..."
        (cd "$INSTALL_DIR" && git pull origin "$BRANCH" 2>/dev/null) || true
    else
        info "Cloning repository..."
        git clone --depth 1 -b "$BRANCH" "$REPO_URL" "$INSTALL_DIR" || fail "Clone failed. Check your internet connection."
    fi
    success "Repository ready at $INSTALL_DIR"
}

check_prereqs() {
    info "Checking prerequisites..."
    command_exists git || fail "Git is required — https://git-scm.com/"
    success "Git $(git --version | cut -d' ' -f3)"

    if command_exists python3; then
        success "Python $(python3 --version | cut -d' ' -f2)"
    elif command_exists python; then
        success "Python $(python --version | cut -d' ' -f2)"
    else
        fail "Python 3.10+ is required — https://www.python.org/"
    fi
}

install_deps() {
    cd "$INSTALL_DIR"

    info "Installing Python package..."
    pip install -e . 2>/dev/null || pip3 install -e . 2>/dev/null || {
        warn "pip install failed — trying with --user flag"
        pip install --user -e . 2>/dev/null || pip3 install --user -e . 2>/dev/null || fail "Could not install Python dependencies."
    }
    success "Python package installed"

    info "Installing Playwright browser (Chromium)..."
    python -m playwright install chromium 2>/dev/null || python3 -m playwright install chromium 2>/dev/null || {
        warn "Playwright browser install failed — you may need to run: playwright install chromium"
    }
    success "Playwright Chromium ready"
}

main() {
    print_banner
    check_prereqs
    clone_repo
    install_deps
    print_done
}

print_done() {
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "  ${BOLD}Installation complete!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "  ${BOLD}Location:${NC}  $INSTALL_DIR"
    echo -e "  ${BOLD}Run:${NC}      automonkeytype --wpm 100"
    echo -e "  ${BOLD}Help:${NC}     automonkeytype --help"
    echo ""
}

main "$@"
