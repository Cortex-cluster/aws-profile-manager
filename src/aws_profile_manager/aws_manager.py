"""
AWS Configuration & Credentials Manager
Handles reading, modifying, renaming, deleting, and testing AWS profiles.
"""

import os
import shutil
import subprocess
import json
import configparser
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

STANDARD_REGIONS = [
    "us-east-1",
    "us-east-2",
    "us-west-1",
    "us-west-2",
    "af-south-1",
    "ap-east-1",
    "ap-south-1",
    "ap-south-2",
    "ap-southeast-1",
    "ap-southeast-2",
    "ap-southeast-3",
    "ap-southeast-4",
    "ap-northeast-1",
    "ap-northeast-2",
    "ap-northeast-3",
    "ca-central-1",
    "ca-west-1",
    "eu-central-1",
    "eu-central-2",
    "eu-west-1",
    "eu-west-2",
    "eu-west-3",
    "eu-north-1",
    "eu-south-1",
    "eu-south-2",
    "il-central-1",
    "me-south-1",
    "me-central-1",
    "sa-east-1",
]

OUTPUT_FORMATS = ["json", "yaml", "yaml-stream", "text", "table"]


class AWSConfigManager:
    def __init__(self, aws_dir: Optional[Path] = None):
        self.aws_dir = aws_dir or (Path.home() / ".aws")
        self.credentials_path = self.aws_dir / "credentials"
        self.config_path = self.aws_dir / "config"
        self.backup_dir = self.aws_dir / "backups"

    def _ensure_dir(self):
        self.aws_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def _create_backup(self):
        self._ensure_dir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if self.credentials_path.exists():
            shutil.copy2(
                self.credentials_path,
                self.backup_dir / f"credentials_{timestamp}.bak",
            )
        if self.config_path.exists():
            shutil.copy2(
                self.config_path,
                self.backup_dir / f"config_{timestamp}.bak",
            )

    def _load_parser(self, path: Path) -> configparser.ConfigParser:
        parser = configparser.ConfigParser()
        parser.optionxform = str  # Preserve casing of options
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                parser.read_file(f)
        return parser

    def _save_parser(self, parser: configparser.ConfigParser, path: Path):
        self._ensure_dir()
        with open(path, "w", encoding="utf-8") as f:
            parser.write(f, space_around_delimiters=True)
        try:
            os.chmod(path, 0o600)
        except OSError:
            pass

    def get_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Returns a dict mapping profile_name -> profile_info dictionary."""
        cred_parser = self._load_parser(self.credentials_path)
        conf_parser = self._load_parser(self.config_path)

        profiles: Dict[str, Dict[str, Any]] = {}

        # 1. Read from credentials
        for sec in cred_parser.sections():
            name = sec.strip()
            if name not in profiles:
                profiles[name] = {
                    "name": name,
                    "aws_access_key_id": "",
                    "aws_secret_access_key": "",
                    "aws_session_token": "",
                    "region": "",
                    "output": "json",
                    "extra_cred": {},
                    "extra_conf": {},
                }
            for k, v in cred_parser.items(sec):
                k_lower = k.lower()
                if k_lower == "aws_access_key_id":
                    profiles[name]["aws_access_key_id"] = v
                elif k_lower == "aws_secret_access_key":
                    profiles[name]["aws_secret_access_key"] = v
                elif k_lower == "aws_session_token":
                    profiles[name]["aws_session_token"] = v
                else:
                    profiles[name]["extra_cred"][k] = v

        # 2. Read from config
        for sec in conf_parser.sections():
            sec_clean = sec.strip()
            if sec_clean.lower().startswith("profile "):
                name = sec_clean[8:].strip()
            else:
                name = sec_clean

            if name not in profiles:
                profiles[name] = {
                    "name": name,
                    "aws_access_key_id": "",
                    "aws_secret_access_key": "",
                    "aws_session_token": "",
                    "region": "",
                    "output": "json",
                    "extra_cred": {},
                    "extra_conf": {},
                }

            for k, v in conf_parser.items(sec):
                k_lower = k.lower()
                if k_lower == "region":
                    profiles[name]["region"] = v
                elif k_lower == "output":
                    profiles[name]["output"] = v
                elif k_lower == "aws_access_key_id" and not profiles[name]["aws_access_key_id"]:
                    profiles[name]["aws_access_key_id"] = v
                elif k_lower == "aws_secret_access_key" and not profiles[name]["aws_secret_access_key"]:
                    profiles[name]["aws_secret_access_key"] = v
                else:
                    profiles[name]["extra_conf"][k] = v

        return profiles

    def save_profile(
        self,
        name: str,
        access_key: str,
        secret_key: str,
        region: str = "",
        output_format: str = "json",
        session_token: str = "",
        extra_cred: Optional[Dict[str, str]] = None,
        extra_conf: Optional[Dict[str, str]] = None,
    ) -> None:
        """Create or update a profile."""
        name = name.strip()
        if not name:
            raise ValueError("Profile name cannot be empty.")

        self._create_backup()

        cred_parser = self._load_parser(self.credentials_path)
        conf_parser = self._load_parser(self.config_path)

        # Credentials section
        cred_sec = name
        if not cred_parser.has_section(cred_sec):
            cred_parser.add_section(cred_sec)

        if access_key.strip():
            cred_parser.set(cred_sec, "aws_access_key_id", access_key.strip())
        elif cred_parser.has_option(cred_sec, "aws_access_key_id"):
            cred_parser.remove_option(cred_sec, "aws_access_key_id")

        if secret_key.strip():
            cred_parser.set(cred_sec, "aws_secret_access_key", secret_key.strip())
        elif cred_parser.has_option(cred_sec, "aws_secret_access_key"):
            cred_parser.remove_option(cred_sec, "aws_secret_access_key")

        if session_token.strip():
            cred_parser.set(cred_sec, "aws_session_token", session_token.strip())
        elif cred_parser.has_option(cred_sec, "aws_session_token"):
            cred_parser.remove_option(cred_sec, "aws_session_token")

        if extra_cred:
            for k, v in extra_cred.items():
                cred_parser.set(cred_sec, k, v)

        # Config section
        conf_sec = "default" if name.lower() == "default" else f"profile {name}"
        # If old format exists without "profile ", find it
        if not conf_parser.has_section(conf_sec):
            if conf_parser.has_section(name):
                conf_sec = name
            else:
                conf_parser.add_section(conf_sec)

        if region.strip():
            conf_parser.set(conf_sec, "region", region.strip())
        elif conf_parser.has_option(conf_sec, "region"):
            conf_parser.remove_option(conf_sec, "region")

        if output_format.strip():
            conf_parser.set(conf_sec, "output", output_format.strip())
        elif conf_parser.has_option(conf_sec, "output"):
            conf_parser.remove_option(conf_sec, "output")

        if extra_conf:
            for k, v in extra_conf.items():
                conf_parser.set(conf_sec, k, v)

        self._save_parser(cred_parser, self.credentials_path)
        self._save_parser(conf_parser, self.config_path)

    def rename_profile(self, old_name: str, new_name: str) -> None:
        """Rename an existing profile across credentials and config."""
        old_name = old_name.strip()
        new_name = new_name.strip()

        if not old_name or not new_name:
            raise ValueError("Profile names cannot be empty.")
        if old_name == new_name:
            return

        current_profiles = self.get_profiles()
        if old_name not in current_profiles:
            raise ValueError(f"Profile '{old_name}' does not exist.")
        if new_name in current_profiles:
            raise ValueError(f"A profile named '{new_name}' already exists.")

        self._create_backup()

        # Update credentials
        cred_parser = self._load_parser(self.credentials_path)
        if cred_parser.has_section(old_name):
            items = list(cred_parser.items(old_name))
            cred_parser.remove_section(old_name)
            cred_parser.add_section(new_name)
            for k, v in items:
                cred_parser.set(new_name, k, v)
            self._save_parser(cred_parser, self.credentials_path)

        # Update config
        conf_parser = self._load_parser(self.config_path)
        old_conf_sec = None
        for sec in conf_parser.sections():
            sec_clean = sec.strip()
            sec_name = sec_clean[8:].strip() if sec_clean.lower().startswith("profile ") else sec_clean
            if sec_name == old_name:
                old_conf_sec = sec
                break

        if old_conf_sec:
            items = list(conf_parser.items(old_conf_sec))
            conf_parser.remove_section(old_conf_sec)
            new_conf_sec = "default" if new_name.lower() == "default" else f"profile {new_name}"
            conf_parser.add_section(new_conf_sec)
            for k, v in items:
                conf_parser.set(new_conf_sec, k, v)
            self._save_parser(conf_parser, self.config_path)

    def delete_profile(self, name: str) -> None:
        """Delete profile from credentials and config."""
        name = name.strip()
        if not name:
            raise ValueError("Profile name cannot be empty.")

        self._create_backup()

        # Remove from credentials
        cred_parser = self._load_parser(self.credentials_path)
        if cred_parser.has_section(name):
            cred_parser.remove_section(name)
            self._save_parser(cred_parser, self.credentials_path)

        # Remove from config
        conf_parser = self._load_parser(self.config_path)
        to_remove = []
        for sec in conf_parser.sections():
            sec_clean = sec.strip()
            sec_name = sec_clean[8:].strip() if sec_clean.lower().startswith("profile ") else sec_clean
            if sec_name == name:
                to_remove.append(sec)

        for sec in to_remove:
            conf_parser.remove_section(sec)

        if to_remove:
            self._save_parser(conf_parser, self.config_path)

    def test_profile(self, name: str) -> Tuple[bool, Dict[str, Any], str]:
        """Runs aws sts get-caller-identity --profile <name>."""
        name = name.strip()
        cmd = ["aws", "sts", "get-caller-identity", "--profile", name, "--output", "json"]
        try:
            res = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=12,
            )
            if res.returncode == 0:
                try:
                    data = json.loads(res.stdout)
                    return True, data, ""
                except json.JSONDecodeError:
                    return True, {"raw": res.stdout}, ""
            else:
                return False, {}, res.stderr.strip() or res.stdout.strip()
        except FileNotFoundError:
            return False, {}, "AWS CLI executable ('aws') not found in PATH."
        except subprocess.TimeoutExpired:
            return False, {}, "Connection timed out while contacting AWS STS (12s)."
        except Exception as e:
            return False, {}, str(e)
