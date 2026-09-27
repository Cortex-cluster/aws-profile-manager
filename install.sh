#!/usr/bin/env bash
# ==============================================================================
# AWS Profile Manager - Universal Installer
# ==============================================================================

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BLUE}${BOLD}"
cat << 'EOF'
     ___ _       ______  ____             _____ __        
    /   | |     / / ___// __ \_________  / __(_) /__      
   / /| | | /| / /\__ \/ /_/ / ___/ __ \/ /_/ / / _ \     
  / ___ | |/ |/ /___/ / ____/ /  / /_/ / __/ / /  __/     
 /_/  |_|__/|__//____/_/   /_/   \____/_/ /_/_/\___/      
                   PROFILE MANAGER                         
EOF
echo -e "${NC}"
echo -e "${BOLD}Installing AWS Profile Manager...${NC}\n"

# Check root vs user mode
if [ "$EUID" -eq 0 ]; then
    INSTALL_MODE="system"
    PREFIX="/usr"
    BIN_DIR="/usr/local/bin"
    SHARE_DIR="/usr/share/aws-profile-manager"
    APPS_DIR="/usr/share/applications"
    ICONS_DIR="/usr/share/icons/hicolor"
else
    INSTALL_MODE="user"
    PREFIX="$HOME/.local"
    BIN_DIR="$HOME/.local/bin"
    SHARE_DIR="$HOME/.local/share/aws-profile-manager"
    APPS_DIR="$HOME/.local/share/applications"
    ICONS_DIR="$HOME/.local/share/icons/hicolor"
fi

echo -e "• Installation mode: ${YELLOW}${INSTALL_MODE}${NC} (prefix: $PREFIX)"

# Check Dependencies
echo -e "• Checking dependencies..."
MISSING_DEPS=""

if ! command -v python3 &>/dev/null; then
    MISSING_DEPS="$MISSING_DEPS python3"
fi

if ! python3 -c "import gi; gi.require_version('Gtk', '3.0')" &>/dev/null; then
    MISSING_DEPS="$MISSING_DEPS python3-gi gir1.2-gtk-3.0"
fi

if [ -n "$MISSING_DEPS" ]; then
    echo -e "${YELLOW}Warning: Missing required dependencies:${NC} $MISSING_DEPS"
    if command -v apt-get &>/dev/null; then
        echo -e "You can install them on Ubuntu/Debian with:"
        echo -e "  ${BOLD}sudo apt update && sudo apt install -y python3-gi gir1.2-gtk-3.0${NC}\n"
    fi
else
    echo -e "  ${GREEN}✔${NC} All dependencies verified (Python 3, PyGObject, GTK 3)"
fi

# Detect repository root / script directory or curl download
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd || true)"
TMP_CLONE=""

if [ ! -d "$SCRIPT_DIR/src/aws_profile_manager" ]; then
    echo -e "• Downloading latest release from GitHub..."
    TMP_CLONE="$(mktemp -d)"
    git clone --depth 1 https://github.com/Cortex-cluster/aws-profile-manager.git "$TMP_CLONE"
    SCRIPT_DIR="$TMP_CLONE"
fi

# Prepare directories
mkdir -p "$BIN_DIR" "$SHARE_DIR/src" "$APPS_DIR"

# Install application files
echo -e "• Installing application files..."
rm -rf "$SHARE_DIR/src"
mkdir -p "$SHARE_DIR/src/aws_profile_manager"
cp -r "$SCRIPT_DIR/src/aws_profile_manager/"* "$SHARE_DIR/src/aws_profile_manager/"

# Install launcher binary
cat << 'LAUNCHER_EOF' > "$BIN_DIR/aws-profile-manager"
#!/usr/bin/env bash
exec /usr/bin/python3 -c "
import sys
from pathlib import Path
candidates = [
    Path('/usr/share/aws-profile-manager/src'),
    Path.home() / '.local/share/aws-profile-manager/src',
]
for p in candidates:
    if p.exists():
        sys.path.insert(0, str(p / 'aws_profile_manager'))
        sys.path.insert(0, str(p))
        break
from main import main
sys.exit(main())
" "$@"
LAUNCHER_EOF
chmod +x "$BIN_DIR/aws-profile-manager"

# Install Icons
echo -e "• Installing application icons..."
for sz in 32 48 64 128 256 512; do
    mkdir -p "$ICONS_DIR/${sz}x${sz}/apps"
done
mkdir -p "$ICONS_DIR/scalable/apps"

if [ -f "$SCRIPT_DIR/assets/aws-profile-manager.svg" ]; then
    cp "$SCRIPT_DIR/assets/aws-profile-manager.svg" "$ICONS_DIR/scalable/apps/aws-profile-manager.svg"
fi

if [ -f "$SCRIPT_DIR/assets/aws-profile-manager.png" ]; then
    for sz in 32 48 64 128 256; do
        python3 -c "
import gi; gi.require_version('GdkPixbuf', '2.0'); from gi.repository import GdkPixbuf
try:
    pb = GdkPixbuf.Pixbuf.new_from_file_at_scale('$SCRIPT_DIR/assets/aws-profile-manager.png', $sz, $sz, True)
    pb.savev('$ICONS_DIR/${sz}x${sz}/apps/aws-profile-manager.png', 'png', [], [])
except Exception:
    pass
" 2>/dev/null || true
    done
fi

# Install Desktop Entry
echo -e "• Installing desktop entry..."
cat << DESKTOP_EOF > "$APPS_DIR/aws-profile-manager.desktop"
[Desktop Entry]
Version=1.0
Type=Application
Name=AWS Profile Manager
GenericName=AWS Account Manager
Comment=Manage, rename, delete, test, and protect AWS CLI accounts and credentials
Exec=$BIN_DIR/aws-profile-manager
Icon=aws-profile-manager
Terminal=false
Categories=Development;Settings;Utility;
Keywords=aws;profile;credentials;cloud;amazon;iam;sts;security;
StartupNotify=true
StartupWMClass=aws-profile-manager
DESKTOP_EOF
chmod +x "$APPS_DIR/aws-profile-manager.desktop"

# Optional Desktop Shortcut
if [ -d "$HOME/Desktop" ] && [ "$INSTALL_MODE" = "user" ]; then
    cp "$APPS_DIR/aws-profile-manager.desktop" "$HOME/Desktop/aws-profile-manager.desktop"
    chmod +x "$HOME/Desktop/aws-profile-manager.desktop"
    if command -v gio &>/dev/null; then
        gio set "$HOME/Desktop/aws-profile-manager.desktop" metadata::trusted true 2>/dev/null || true
    fi
fi

# Update Caches
if command -v update-desktop-database &>/dev/null; then
    update-desktop-database "$APPS_DIR" 2>/dev/null || true
fi
if command -v gtk-update-icon-cache &>/dev/null; then
    gtk-update-icon-cache -f -t "$ICONS_DIR" 2>/dev/null || true
fi

# Cleanup temp clone if used
if [ -n "$TMP_CLONE" ] && [ -d "$TMP_CLONE" ]; then
    rm -rf "$TMP_CLONE"
fi

# Ensure bin is in PATH for user
if [ "$INSTALL_MODE" = "user" ] && [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo -e "\n${YELLOW}Note: Add ~/.local/bin to your PATH to run 'aws-profile-manager' anywhere:${NC}"
    echo -e "  echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc\n"
fi

echo -e "\n${GREEN}${BOLD}✔ AWS Profile Manager installed successfully!${NC}"
echo -e "Launch it by searching '${BOLD}AWS Profile Manager${NC}' in your applications, or run:"
echo -e "  ${BOLD}aws-profile-manager &${NC}\n"
