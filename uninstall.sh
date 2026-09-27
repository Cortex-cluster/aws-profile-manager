#!/usr/bin/env bash
# ==============================================================================
# AWS Profile Manager - Uninstaller
# ==============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${RED}${BOLD}Uninstalling AWS Profile Manager...${NC}\n"

# Remove from user locations
rm -f "$HOME/.local/bin/aws-profile-manager"
rm -rf "$HOME/.local/share/aws-profile-manager"
rm -f "$HOME/.local/share/applications/aws-profile-manager.desktop"
rm -f "$HOME/Desktop/aws-profile-manager.desktop"
rm -f "$HOME/.local/share/icons/hicolor/*/apps/aws-profile-manager.*"
rm -f "$HOME/.local/share/icons/aws-profile-manager.*"

# Remove from system locations if run as root
if [ "$EUID" -eq 0 ]; then
    rm -f "/usr/local/bin/aws-profile-manager"
    rm -f "/usr/bin/aws-profile-manager"
    rm -rf "/usr/share/aws-profile-manager"
    rm -f "/usr/share/applications/aws-profile-manager.desktop"
    rm -f "/usr/share/icons/hicolor/*/apps/aws-profile-manager.*"
fi

if command -v update-desktop-database &>/dev/null; then
    update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
fi
if command -v gtk-update-icon-cache &>/dev/null; then
    gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" 2>/dev/null || true
fi

echo -e "${GREEN}${BOLD}✔ AWS Profile Manager has been completely removed.${NC}"
echo -e "Your actual AWS credentials (~/.aws/) remain untouched."
