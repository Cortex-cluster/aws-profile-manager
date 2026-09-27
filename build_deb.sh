#!/usr/bin/env bash
# ==============================================================================
# AWS Profile Manager - Debian Package (.deb) Builder
# ==============================================================================

set -e

VERSION="1.0.0"
PACKAGE_NAME="aws-profile-manager"
ARCH="all"
BUILD_DIR="$(mktemp -d)"
OUTPUT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/dist"

echo "Building Debian package: ${PACKAGE_NAME}_${VERSION}_${ARCH}.deb..."

mkdir -p "$OUTPUT_DIR"
mkdir -p "$BUILD_DIR/DEBIAN"
mkdir -p "$BUILD_DIR/usr/bin"
mkdir -p "$BUILD_DIR/usr/share/aws-profile-manager/src"
mkdir -p "$BUILD_DIR/usr/share/applications"
mkdir -p "$BUILD_DIR/usr/share/icons/hicolor/scalable/apps"
mkdir -p "$BUILD_DIR/usr/share/icons/hicolor/256x256/apps"

# 1. DEBIAN/control
cat << EOF > "$BUILD_DIR/DEBIAN/control"
Package: ${PACKAGE_NAME}
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: ${ARCH}
Depends: python3, python3-gi, gir1.2-gtk-3.0
Suggests: awscli
Maintainer: Pawan Pratap <cluster.cortex@gmail.com>
Description: Native Linux Desktop GUI for AWS CLI Accounts and Profiles
 AWS Profile Manager provides an intuitive, modern GTK desktop interface
 to view, create, rename, delete, and test AWS accounts and credentials
 with system password security for secret access keys.
EOF

# 2. DEBIAN/postinst
cat << 'EOF' > "$BUILD_DIR/DEBIAN/postinst"
#!/bin/sh
set -e
if [ -x /usr/bin/update-desktop-database ]; then
    /usr/bin/update-desktop-database -q /usr/share/applications || true
fi
if [ -x /usr/bin/gtk-update-icon-cache ]; then
    /usr/bin/gtk-update-icon-cache -q -f -t /usr/share/icons/hicolor || true
fi
exit 0
EOF
chmod 755 "$BUILD_DIR/DEBIAN/postinst"

# 3. Source files
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp -r "$SCRIPT_DIR/src/aws_profile_manager" "$BUILD_DIR/usr/share/aws-profile-manager/src/"

# 4. Binary launcher
cat << 'EOF' > "$BUILD_DIR/usr/bin/aws-profile-manager"
#!/usr/bin/env bash
export PYTHONPATH="/usr/share/aws-profile-manager/src:/usr/share/aws-profile-manager/src/aws_profile_manager:$PYTHONPATH"
exec /usr/bin/python3 -m aws_profile_manager.main "$@"
EOF
chmod 755 "$BUILD_DIR/usr/bin/aws-profile-manager"

# 5. Desktop Entry
cp "$SCRIPT_DIR/assets/aws-profile-manager.desktop" "$BUILD_DIR/usr/share/applications/"
chmod 644 "$BUILD_DIR/usr/share/applications/aws-profile-manager.desktop"

# 6. Icons
cp "$SCRIPT_DIR/assets/aws-profile-manager.svg" "$BUILD_DIR/usr/share/icons/hicolor/scalable/apps/"
cp "$SCRIPT_DIR/assets/aws-profile-manager.png" "$BUILD_DIR/usr/share/icons/hicolor/256x256/apps/"

# 7. Build package
dpkg-deb --build --root-owner-group "$BUILD_DIR" "$OUTPUT_DIR/${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"

# Clean up
rm -rf "$BUILD_DIR"

echo "✔ Built successfully: $OUTPUT_DIR/${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"
