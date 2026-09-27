"""
Authentication helper using Linux system credentials.
"""

import os
import getpass
import subprocess


def get_current_username() -> str:
    try:
        return getpass.getuser()
    except Exception:
        return os.environ.get("USER", "user")


def verify_system_password(password: str) -> bool:
    """
    Verifies the provided system password using standard PAM/sudo verification.
    Immediately resets sudo timestamp afterwards so no elevated state persists.
    """
    if not password:
        return False
    try:
        proc = subprocess.run(
            ["sudo", "-k", "-S", "-p", "", "true"],
            input=(password + "\n").encode("utf-8"),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=8,
        )
        # Ensure timestamp is cleared
        subprocess.run(["sudo", "-k"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return proc.returncode == 0
    except Exception:
        return False
