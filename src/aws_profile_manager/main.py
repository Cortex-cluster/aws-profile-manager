#!/usr/bin/env python3
"""
Entry point for AWS Profile Manager
"""

import sys
import signal
from pathlib import Path

# Add local directory to module search path
app_dir = Path(__file__).parent.resolve()
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk, GLib

from ui import AWSProfileManagerApp


class AWSProfileManager(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id="com.github.pawan.aws-profile-manager",
            flags=0
        )
        self.window = None

    def do_activate(self):
        if not self.window:
            self.window = AWSProfileManagerApp(self)
        self.window.present()


def main():
    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    GLib.set_prgname("aws-profile-manager")
    GLib.set_application_name("AWS Profile Manager")
    Gtk.Window.set_default_icon_name("aws-profile-manager")
    app = AWSProfileManager()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
