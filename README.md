# AWS Profile Manager ☁️🔑

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-Linux-orange.svg)](https://www.linux.org/)
[![UI: GTK3](https://img.shields.io/badge/UI-GTK%203-blue.svg)](https://www.gtk.org/)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/)

**AWS Profile Manager** is a native, modern Linux desktop application designed to easily manage, switch, test, and protect your AWS CLI account profiles and credentials.

Built with native GTK 3 / Adwaita and styled with AWS colorways, it offers full security for sensitive keys by integrating directly with your **Linux system password**.

---

## ✨ Features

- **Multi-Account Overview**: Lists all profiles from `~/.aws/credentials` and `~/.aws/config` with status badges, regions, and vibrant avatars.
- 🔒 **System Password Security**: AWS Secret Access Keys and session tokens are **never exposed by default**. They are protected behind a native Linux system password authentication modal.
- ⚡ **Live STS Connection Testing**: Test any account live against AWS STS (`aws sts get-caller-identity`) with progress indicators, returning your verified AWS Account ID, IAM Caller ARN, and User ID.
- ✏️ **Rename & Reorganize**: Safely rename profiles across both `credentials` and `config` simultaneously.
- ➕ **Add & Delete Accounts**: Quickly configure new profiles with access keys, regions, and formats.
- 🛡️ **Automated Safety Backups**: Creates timestamped backups in `~/.aws/backups/` whenever modifications are saved.
- 📋 **Terminal Quick-Copy**: Copy `export AWS_PROFILE=<name>` with a single click to activate accounts in your terminal.
- ⌨️ **Keyboard Shortcuts**: Designed for efficiency (`Ctrl+N` for New, `Ctrl+R` for Refresh, `Ctrl+S` for Save, `F2` to Rename).

---

## 🚀 Installation

### Option 1: One-Line Installer (Recommended)

Run this single command in your terminal to install the latest version automatically:

```bash
curl -sSL https://raw.githubusercontent.com/Cortex-cluster/aws-profile-manager/main/install.sh | bash
```

---

### Option 2: Debian / Ubuntu Package (`.deb`)

Download the latest `.deb` package from the [Releases](https://github.com/Cortex-cluster/aws-profile-manager/releases) page or build it locally, then install:

```bash
sudo apt install ./aws-profile-manager_1.0.0_all.deb
```

---

### Option 3: Install from Source

```bash
# Clone the repository
git clone https://github.com/Cortex-cluster/aws-profile-manager.git
cd aws-profile-manager

# Run the installer
./install.sh
```

---

## 🏃 Running the Application

After installation, you can launch AWS Profile Manager in several ways:

1. **Desktop Shortcut**: Double-click the **AWS Profile Manager** icon on your Desktop.
2. **Application Menu**: Press `Super` (Windows key) and type **AWS Profile Manager**.
3. **Terminal**:
   ```bash
   aws-profile-manager &
   ```

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
| :--- | :--- |
| <kbd>Ctrl</kbd> + <kbd>N</kbd> | Create New Profile |
| <kbd>Ctrl</kbd> + <kbd>R</kbd> | Reload Profiles from disk |
| <kbd>Ctrl</kbd> + <kbd>S</kbd> | Save Profile Changes |
| <kbd>F2</kbd> | Rename Selected Profile |
| <kbd>Ctrl</kbd> + <kbd>D</kbd> | Delete Selected Profile |

---

## 🛠️ Requirements

- **Linux** (Ubuntu, Debian, Fedora, Arch, Linux Mint, Pop!_OS, etc.)
- **Python** 3.8 or later
- **GTK 3** & **PyGObject** (`python3-gi`, `gir1.2-gtk-3.0`)
- **AWS CLI** (`aws`) *(recommended for STS connection testing)*

On Ubuntu / Debian, you can install the runtime dependencies with:
```bash
sudo apt update && sudo apt install -y python3 python3-gi gir1.2-gtk-3.0
```

---

## 🗑️ Uninstallation

To completely remove the application and its icons:

```bash
curl -sSL https://raw.githubusercontent.com/Cortex-cluster/aws-profile-manager/main/uninstall.sh | bash
```

*(Note: Your actual AWS configuration files in `~/.aws/` will never be deleted by the uninstaller).*

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
