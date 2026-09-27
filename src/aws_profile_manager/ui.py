"""
AWS Profile Manager - Beautiful Modern GTK 3 UI
Enhanced with Adwaita / AWS styling and System Password Protection.
"""

import os
import sys
import hashlib
import threading
from pathlib import Path
from typing import Optional, Dict, Any

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("GdkPixbuf", "2.0")
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf

from aws_manager import AWSConfigManager, STANDARD_REGIONS, OUTPUT_FORMATS
import auth

APP_DIR = Path(__file__).parent.resolve()

def get_icon_path() -> Optional[Path]:
    candidates = [
        Path.home() / ".local/share/icons/hicolor/256x256/apps/aws-profile-manager.png",
        Path.home() / ".local/share/icons/aws-profile-manager.svg",
        Path("/usr/share/icons/hicolor/256x256/apps/aws-profile-manager.png"),
        Path("/usr/share/icons/hicolor/scalable/apps/aws-profile-manager.svg"),
        APP_DIR.parent.parent / "assets/aws-profile-manager.png",
        APP_DIR.parent.parent / "assets/aws-profile-manager.svg",
        Path("/usr/share/aws-profile-manager/assets/aws-profile-manager.png"),
    ]
    for p in candidates:
        if p.exists():
            return p
    return None

ICON_PATH = get_icon_path()

AVATAR_GRADIENTS = [
    ("#FF9900", "#FF5500"),  # AWS Orange
    ("#1A73E8", "#0D47A1"),  # Google Blue
    ("#9333EA", "#581C87"),  # Purple
    ("#059669", "#064E3B"),  # Emerald Green
    ("#D97706", "#78350F"),  # Amber
    ("#DC2626", "#7F1D1D"),  # Red
    ("#0284C7", "#0C4A6E"),  # Sky
    ("#4F46E5", "#312E81"),  # Indigo
]

APP_CSS = b"""
/* Main Container & Background */
.main-window {
    background-color: @theme_bg_color;
}

/* Sidebar Styling */
.sidebar-box {
    background-color: alpha(@theme_bg_color, 0.95);
    border-right: 1px solid alpha(@borders, 0.5);
}
.sidebar-list {
    background-color: transparent;
}
.sidebar-row {
    padding: 10px 12px;
    border-radius: 8px;
    margin: 3px 6px;
    transition: all 180ms ease;
    border: 1px solid transparent;
}
.sidebar-row:hover {
    background-color: alpha(@theme_fg_color, 0.05);
}
.sidebar-row:selected {
    background-color: alpha(#3584e4, 0.15);
    border: 1px solid alpha(#3584e4, 0.4);
    color: @theme_fg_color;
}

/* Badges */
.badge-default {
    background-color: #2ec27e;
    color: #ffffff;
    border-radius: 5px;
    padding: 2px 6px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.5px;
}
.badge-region {
    background-color: alpha(#3584e4, 0.12);
    color: #1c71d8;
    border-radius: 5px;
    padding: 2px 7px;
    font-size: 11px;
    font-weight: 600;
}
.badge-locked {
    background-color: alpha(#f5c211, 0.18);
    color: #c67800;
    border-radius: 5px;
    padding: 2px 6px;
    font-size: 10px;
    font-weight: 600;
}
.badge-unlocked {
    background-color: alpha(#2ec27e, 0.15);
    color: #26a269;
    border-radius: 5px;
    padding: 2px 6px;
    font-size: 10px;
    font-weight: 600;
}

/* Hero Section */
.hero-box {
    background: linear-gradient(135deg, alpha(#232F3E, 0.9), alpha(#131921, 0.95));
    color: #ffffff;
    border-radius: 12px;
    padding: 18px 22px;
    margin-bottom: 6px;
    border: 1px solid alpha(#FF9900, 0.3);
}
.hero-title {
    font-size: 22px;
    font-weight: 800;
    color: #ffffff;
}
.hero-subtitle {
    font-size: 13px;
    color: #d0d7de;
}

/* Modern Cards */
.modern-card {
    background-color: alpha(@theme_bg_color, 0.85);
    border: 1px solid alpha(@borders, 0.65);
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 12px;
}
.card-header-title {
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 0.2px;
}

/* Monospace inputs */
.mono-entry {
    font-family: 'JetBrains Mono', 'Fira Code', 'DejaVu Sans Mono', monospace;
    font-size: 13px;
}
.masked-entry {
    letter-spacing: 2px;
    font-size: 15px;
    color: alpha(@theme_fg_color, 0.6);
}

/* Terminal snippet box */
.terminal-box {
    background-color: #1e1e2e;
    color: #a6e3a1;
    border-radius: 8px;
    padding: 10px 14px;
    font-family: monospace;
    font-size: 13px;
    border: 1px solid #313244;
}

/* Test results */
.test-status-box {
    border-radius: 10px;
    padding: 14px 18px;
    color: @theme_fg_color;
}
.test-loading-box {
    background-color: alpha(#3584e4, 0.14);
    border: 1.5px solid #3584e4;
    border-radius: 10px;
    padding: 14px 18px;
    color: @theme_fg_color;
}
.test-success-box {
    background-color: alpha(#2ec27e, 0.16);
    border: 1.5px solid #2ec27e;
    border-radius: 10px;
    padding: 14px 18px;
    color: @theme_fg_color;
}
.test-error-box {
    background-color: alpha(#e01b24, 0.16);
    border: 1.5px solid #e01b24;
    border-radius: 10px;
    padding: 14px 18px;
    color: @theme_fg_color;
}

/* Custom buttons */
.btn-unlock {
    background-color: alpha(#FF9900, 0.18);
    color: #c67800;
    border: 1px solid alpha(#FF9900, 0.4);
    border-radius: 6px;
    font-weight: 600;
    padding: 6px 14px;
}
.btn-unlock:hover {
    background-color: #FF9900;
    color: #ffffff;
}
.btn-lock {
    background-color: alpha(#77767b, 0.15);
    border-radius: 6px;
    padding: 6px 14px;
}

/* Avatar Label & Colors */
.avatar-badge {
    border-radius: 18px;
    min-width: 36px;
    min-height: 36px;
    font-weight: bold;
    color: #ffffff;
}
.hero-avatar {
    border-radius: 24px;
    min-width: 48px;
    min-height: 48px;
    font-size: 16px;
    font-weight: bold;
    color: #ffffff;
}
.avatar-0 { background: linear-gradient(135deg, #FF9900, #FF5500); }
.avatar-1 { background: linear-gradient(135deg, #1A73E8, #0D47A1); }
.avatar-2 { background: linear-gradient(135deg, #9333EA, #581C87); }
.avatar-3 { background: linear-gradient(135deg, #059669, #064E3B); }
.avatar-4 { background: linear-gradient(135deg, #D97706, #78350F); }
.avatar-5 { background: linear-gradient(135deg, #DC2626, #7F1D1D); }
.avatar-6 { background: linear-gradient(135deg, #0284C7, #0C4A6E); }
.avatar-7 { background: linear-gradient(135deg, #4F46E5, #312E81); }
"""


def copy_to_clipboard(text: str):
    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
    clipboard.set_text(text, -1)


def get_profile_initials(name: str) -> str:
    cleaned = "".join(c for c in name if c.isalnum())
    if not cleaned:
        return "AW"
    if len(cleaned) == 1:
        return cleaned.upper()
    return (cleaned[0] + cleaned[1]).upper()


def get_profile_color_index(name: str) -> int:
    return int(hashlib.md5(name.encode("utf-8")).hexdigest(), 16) % 8


class SystemAuthDialog(Gtk.Dialog):
    """Native authentication dialog requiring the Linux user password."""
    def __init__(self, parent: Gtk.Window, profile_name: str):
        super().__init__(
            title="Authentication Required",
            transient_for=parent,
            flags=Gtk.DialogFlags.MODAL,
        )
        self.set_default_size(440, 240)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.profile_name = profile_name
        self.authenticated = False

        self.btn_cancel = self.add_button("_Cancel", Gtk.ResponseType.CANCEL)
        self.btn_unlock = self.add_button("_Unlock Credentials", Gtk.ResponseType.OK)
        self.btn_unlock.get_style_context().add_class("suggested-action")
        self.btn_unlock.set_sensitive(False)

        content = self.get_content_area()
        content.set_margin_start(24)
        content.set_margin_end(24)
        content.set_margin_top(20)
        content.set_margin_bottom(16)
        content.set_spacing(14)

        # Header with Shield Icon & Prompt
        hdr_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        icon_shield = Gtk.Image.new_from_icon_name("dialog-password-symbolic", Gtk.IconSize.DIALOG)
        icon_shield.set_pixel_size(48)
        hdr_box.pack_start(icon_shield, False, False, 0)

        vbox_txt = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        lbl_head = Gtk.Label()
        lbl_head.set_markup("<b><big>Authentication Required</big></b>")
        lbl_head.set_halign(Gtk.Align.START)
        vbox_txt.pack_start(lbl_head, False, False, 0)

        lbl_sub = Gtk.Label()
        lbl_sub.set_markup(
            f"Enter your system password to view secret credentials for AWS profile "
            f"<b>{GLib.markup_escape_text(profile_name)}</b>."
        )
        lbl_sub.set_line_wrap(True)
        lbl_sub.set_halign(Gtk.Align.START)
        vbox_txt.pack_start(lbl_sub, False, False, 0)
        hdr_box.pack_start(vbox_txt, True, True, 0)
        content.pack_start(hdr_box, False, False, 0)

        # User row
        user_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        user_box.set_margin_top(4)
        icon_user = Gtk.Image.new_from_icon_name("avatar-default-symbolic", Gtk.IconSize.BUTTON)
        user_box.pack_start(icon_user, False, False, 0)
        username = auth.get_current_username()
        lbl_user = Gtk.Label(label=f"User: {username}")
        lbl_user.get_style_context().add_class("dim-label")
        user_box.pack_start(lbl_user, False, False, 0)
        content.pack_start(user_box, False, False, 0)

        # Password Entry
        self.entry_pass = Gtk.Entry()
        self.entry_pass.set_visibility(False)
        self.entry_pass.set_placeholder_text("System password")
        self.entry_pass.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY, "dialog-password-symbolic")
        self.entry_pass.connect("changed", self._on_pass_changed)
        self.entry_pass.connect("activate", lambda e: self._attempt_auth())
        content.pack_start(self.entry_pass, False, False, 0)

        # Error / Status message & spinner
        self.status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.spinner = Gtk.Spinner()
        self.status_box.pack_start(self.spinner, False, False, 0)
        self.lbl_status = Gtk.Label()
        self.lbl_status.set_line_wrap(True)
        self.lbl_status.set_halign(Gtk.Align.START)
        self.status_box.pack_start(self.lbl_status, True, True, 0)
        self.status_box.set_no_show_all(True)
        content.pack_start(self.status_box, False, False, 0)

        # Override OK button click to verify synchronously or with feedback
        self.btn_unlock.connect("clicked", lambda b: self._attempt_auth())

        self.show_all()

    def _on_pass_changed(self, entry):
        val = entry.get_text()
        self.btn_unlock.set_sensitive(bool(val.strip()))
        self.status_box.hide()

    def _attempt_auth(self):
        pwd = self.entry_pass.get_text()
        if not pwd:
            return

        self.btn_unlock.set_sensitive(False)
        self.btn_cancel.set_sensitive(False)
        self.entry_pass.set_sensitive(False)

        self.status_box.show()
        self.spinner.show()
        self.spinner.start()
        self.lbl_status.set_markup("<i>Verifying system password...</i>")

        # Verify password in background thread
        def do_verify():
            is_valid = auth.verify_system_password(pwd)
            GLib.idle_add(self._on_verify_done, is_valid)

        threading.Thread(target=do_verify, daemon=True).start()

    def _on_verify_done(self, is_valid: bool):
        self.spinner.stop()
        self.spinner.hide()
        self.btn_cancel.set_sensitive(True)
        self.entry_pass.set_sensitive(True)

        if is_valid:
            self.authenticated = True
            self.response(Gtk.ResponseType.OK)
        else:
            self.btn_unlock.set_sensitive(True)
            self.entry_pass.set_text("")
            self.lbl_status.set_markup("<span color='#e01b24'><b>Incorrect password.</b> Please try again.</span>")
            self.entry_pass.grab_focus()


class AWSProfileManagerApp(Gtk.ApplicationWindow):
    def __init__(self, app: Gtk.Application):
        super().__init__(application=app, title="AWS Profile Manager")
        self.set_default_size(980, 680)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.get_style_context().add_class("main-window")

        # Set Window Icon
        self.set_icon_name("aws-profile-manager")
        if ICON_PATH.exists():
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file(str(ICON_PATH))
                self.set_icon(pixbuf)
            except Exception:
                pass

        self.mgr = AWSConfigManager()
        self.profiles: Dict[str, Dict[str, Any]] = {}
        self.selected_profile_name: Optional[str] = None
        self.unlocked_profiles = set()  # Profiles unlocked this session

        self._apply_css()
        self._build_headerbar()
        self._build_main_ui()

        # Keyboard shortcuts
        self.connect("key-press-event", self._on_key_press)

        self.show_all()
        self.reload_profiles()

    def _apply_css(self):
        provider = Gtk.CssProvider()
        provider.load_from_data(APP_CSS)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def _build_headerbar(self):
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.set_title("AWS Profile Manager")
        header.set_subtitle("Secure Multi-Account Manager")
        self.set_titlebar(header)

        # Refresh button
        btn_refresh = Gtk.Button.new_from_icon_name("view-refresh-symbolic", Gtk.IconSize.BUTTON)
        btn_refresh.set_tooltip_text("Reload profiles from ~/.aws (Ctrl+R)")
        btn_refresh.connect("clicked", lambda b: self.reload_profiles())
        header.pack_start(btn_refresh)

        # Add profile button
        btn_add = Gtk.Button.new_with_mnemonic("_New Account")
        img_add = Gtk.Image.new_from_icon_name("list-add-symbolic", Gtk.IconSize.BUTTON)
        btn_add.set_image(img_add)
        btn_add.set_always_show_image(True)
        btn_add.get_style_context().add_class("suggested-action")
        btn_add.set_tooltip_text("Create a new AWS account profile (Ctrl+N)")
        btn_add.connect("clicked", self._on_add_profile_clicked)
        header.pack_end(btn_add)

    def _build_main_ui(self):
        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_vbox)

        # Info notification banner
        self.info_bar = Gtk.InfoBar()
        self.info_bar_label = Gtk.Label()
        self.info_bar_label.set_line_wrap(True)
        self.info_bar.get_content_area().pack_start(self.info_bar_label, True, True, 0)
        self.info_bar.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)
        self.info_bar.connect("response", lambda ib, resp: self.info_bar.hide())
        self.info_bar.set_no_show_all(True)
        main_vbox.pack_start(self.info_bar, False, False, 0)

        # Paned layout (Sidebar on left, Details on right)
        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        paned.set_position(320)
        main_vbox.pack_start(paned, True, True, 0)

        # ---- LEFT SIDEBAR ----
        sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        sidebar_box.get_style_context().add_class("sidebar-box")
        sidebar_box.set_size_request(280, -1)
        sidebar_box.set_margin_start(10)
        sidebar_box.set_margin_end(8)
        sidebar_box.set_margin_top(10)
        sidebar_box.set_margin_bottom(10)

        # Search bar
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search accounts or regions...")
        self.search_entry.connect("search-changed", self._on_search_changed)
        sidebar_box.pack_start(self.search_entry, False, False, 0)

        # Profile List
        scroll_list = Gtk.ScrolledWindow()
        scroll_list.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.profile_listbox = Gtk.ListBox()
        self.profile_listbox.get_style_context().add_class("sidebar-list")
        self.profile_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.profile_listbox.connect("row-selected", self._on_row_selected)
        self.profile_listbox.set_filter_func(self._list_filter_func)
        scroll_list.add(self.profile_listbox)
        sidebar_box.pack_start(scroll_list, True, True, 0)

        # Sidebar footer
        footer_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.lbl_count = Gtk.Label(label="0 profiles")
        self.lbl_count.get_style_context().add_class("dim-label")
        footer_box.pack_start(self.lbl_count, False, False, 4)

        sidebar_box.pack_start(footer_box, False, False, 0)
        paned.pack1(sidebar_box, False, False)

        # ---- RIGHT DETAIL PANE ----
        self.detail_stack = Gtk.Stack()
        self.detail_stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)

        # Empty State
        empty_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        empty_box.set_valign(Gtk.Align.CENTER)
        empty_box.set_halign(Gtk.Align.CENTER)

        empty_icon = Gtk.Image.new_from_icon_name("network-server-symbolic", Gtk.IconSize.DIALOG)
        empty_icon.set_pixel_size(72)
        empty_box.pack_start(empty_icon, False, False, 0)

        lbl_empty_title = Gtk.Label()
        lbl_empty_title.set_markup("<b><big>No AWS Account Selected</big></b>")
        empty_box.pack_start(lbl_empty_title, False, False, 0)

        lbl_empty_sub = Gtk.Label(label="Choose an account from the left sidebar\nor configure a new AWS profile.")
        lbl_empty_sub.set_justify(Gtk.Justification.CENTER)
        lbl_empty_sub.get_style_context().add_class("dim-label")
        empty_box.pack_start(lbl_empty_sub, False, False, 0)

        btn_empty_create = Gtk.Button.new_with_label("+ Add First Account")
        btn_empty_create.get_style_context().add_class("suggested-action")
        btn_empty_create.connect("clicked", self._on_add_profile_clicked)
        empty_box.pack_start(btn_empty_create, False, False, 10)

        self.detail_stack.add_named(empty_box, "empty")

        # Profile Detail Form
        detail_scroll = Gtk.ScrolledWindow()
        detail_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.detail_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        self.detail_container.set_margin_start(22)
        self.detail_container.set_margin_end(22)
        self.detail_container.set_margin_top(16)
        self.detail_container.set_margin_bottom(20)
        detail_scroll.add(self.detail_container)

        self._build_detail_fields()
        self.detail_stack.add_named(detail_scroll, "detail")

        paned.pack2(self.detail_stack, True, False)

    def _build_detail_fields(self):
        # 1. Hero Card: Profile Header & Actions
        hero_card = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        hero_card.get_style_context().add_class("hero-box")

        # Avatar Initial
        self.lbl_hero_avatar = Gtk.Label()
        self.lbl_hero_avatar.set_size_request(48, 48)
        self.lbl_hero_avatar.get_style_context().add_class("avatar-badge")
        hero_card.pack_start(self.lbl_hero_avatar, False, False, 0)

        vbox_hero = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        self.lbl_profile_hero = Gtk.Label()
        self.lbl_profile_hero.get_style_context().add_class("hero-title")
        self.lbl_profile_hero.set_halign(Gtk.Align.START)
        vbox_hero.pack_start(self.lbl_profile_hero, False, False, 0)

        self.lbl_hero_sub = Gtk.Label()
        self.lbl_hero_sub.get_style_context().add_class("hero-subtitle")
        self.lbl_hero_sub.set_halign(Gtk.Align.START)
        vbox_hero.pack_start(self.lbl_hero_sub, False, False, 0)
        hero_card.pack_start(vbox_hero, True, True, 0)

        # Action Buttons in Hero
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        # Test Connection button
        self.btn_test = Gtk.Button.new_with_label("Test STS")
        self.btn_test.set_tooltip_text("Verify AWS credentials live with AWS STS")
        img_test = Gtk.Image.new_from_icon_name("network-wireless-symbolic", Gtk.IconSize.BUTTON)
        self.btn_test.set_image(img_test)
        self.btn_test.set_always_show_image(True)
        self.btn_test.connect("clicked", self._on_test_connection_clicked)
        btn_box.pack_start(self.btn_test, False, False, 0)

        # Rename button
        self.btn_rename = Gtk.Button.new_with_label("Rename")
        self.btn_rename.set_tooltip_text("Rename this profile (F2)")
        img_rename = Gtk.Image.new_from_icon_name("document-edit-symbolic", Gtk.IconSize.BUTTON)
        self.btn_rename.set_image(img_rename)
        self.btn_rename.set_always_show_image(True)
        self.btn_rename.connect("clicked", self._on_rename_clicked)
        btn_box.pack_start(self.btn_rename, False, False, 0)

        # Delete button
        self.btn_delete = Gtk.Button.new_with_label("Delete")
        self.btn_delete.set_tooltip_text("Permanently remove this profile")
        img_del = Gtk.Image.new_from_icon_name("user-trash-symbolic", Gtk.IconSize.BUTTON)
        self.btn_delete.set_image(img_del)
        self.btn_delete.set_always_show_image(True)
        self.btn_delete.get_style_context().add_class("destructive-action")
        self.btn_delete.connect("clicked", self._on_delete_clicked)
        btn_box.pack_start(self.btn_delete, False, False, 0)

        hero_card.pack_end(btn_box, False, False, 0)
        self.detail_container.pack_start(hero_card, False, False, 0)

        # Test Connection Result Box
        self.test_status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
        self.test_status_box.get_style_context().add_class("test-status-box")
        self.test_status_spinner = Gtk.Spinner()
        self.test_status_icon = Gtk.Image()
        self.test_status_box.pack_start(self.test_status_spinner, False, False, 0)
        self.test_status_box.pack_start(self.test_status_icon, False, False, 0)
        self.test_status_label = Gtk.Label()
        self.test_status_label.set_line_wrap(True)
        self.test_status_label.set_halign(Gtk.Align.START)
        self.test_status_label.set_xalign(0.0)
        self.test_status_box.pack_start(self.test_status_label, True, True, 0)

        btn_dismiss_test = Gtk.Button.new_from_icon_name("window-close-symbolic", Gtk.IconSize.BUTTON)
        btn_dismiss_test.set_relief(Gtk.ReliefStyle.NONE)
        btn_dismiss_test.set_tooltip_text("Dismiss status")
        btn_dismiss_test.connect("clicked", lambda b: self.test_status_box.hide())
        self.test_status_box.pack_end(btn_dismiss_test, False, False, 0)
        self.detail_container.pack_start(self.test_status_box, False, False, 0)

        # 2. Card: Security & Credentials
        cred_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        cred_card.get_style_context().add_class("modern-card")

        # Card Title
        hdr_cred = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        lbl_c_icon = Gtk.Image.new_from_icon_name("dialog-password-symbolic", Gtk.IconSize.BUTTON)
        hdr_cred.pack_start(lbl_c_icon, False, False, 0)
        lbl_c_title = Gtk.Label()
        lbl_c_title.set_markup("<b>AWS Access Credentials</b>")
        lbl_c_title.get_style_context().add_class("card-header-title")
        hdr_cred.pack_start(lbl_c_title, False, False, 0)

        self.lbl_lock_status = Gtk.Label(label="LOCKED")
        self.lbl_lock_status.get_style_context().add_class("badge-locked")
        hdr_cred.pack_end(self.lbl_lock_status, False, False, 0)
        cred_card.pack_start(hdr_cred, False, False, 0)

        grid_cred = Gtk.Grid()
        grid_cred.set_row_spacing(12)
        grid_cred.set_column_spacing(14)
        cred_card.pack_start(grid_cred, False, False, 0)

        # Row 0: Access Key ID
        lbl_key = Gtk.Label(label="Access Key ID:")
        lbl_key.set_halign(Gtk.Align.END)
        grid_cred.attach(lbl_key, 0, 0, 1, 1)

        key_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.entry_access_key = Gtk.Entry()
        self.entry_access_key.get_style_context().add_class("mono-entry")
        self.entry_access_key.set_placeholder_text("AKIAIOSFODNN7EXAMPLE")
        self.entry_access_key.set_hexpand(True)
        key_box.pack_start(self.entry_access_key, True, True, 0)

        btn_copy_key = Gtk.Button.new_from_icon_name("edit-copy-symbolic", Gtk.IconSize.BUTTON)
        btn_copy_key.set_tooltip_text("Copy Access Key ID")
        btn_copy_key.connect("clicked", lambda b: self._copy_entry(self.entry_access_key, "Access Key ID"))
        key_box.pack_end(btn_copy_key, False, False, 0)
        grid_cred.attach(key_box, 1, 0, 1, 1)

        # Row 1: Secret Access Key (Password Protected)
        lbl_secret = Gtk.Label(label="Secret Access Key:")
        lbl_secret.set_halign(Gtk.Align.END)
        grid_cred.attach(lbl_secret, 0, 1, 1, 1)

        self.secret_stack = Gtk.Stack()
        self.secret_stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)

        # Locked page
        locked_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.entry_locked_preview = Gtk.Entry()
        self.entry_locked_preview.set_text("••••••••••••••••••••••••••••••••••••••••")
        self.entry_locked_preview.set_editable(False)
        self.entry_locked_preview.set_sensitive(False)
        self.entry_locked_preview.get_style_context().add_class("masked-entry")
        self.entry_locked_preview.set_hexpand(True)
        locked_box.pack_start(self.entry_locked_preview, True, True, 0)

        self.btn_auth_unlock = Gtk.Button.new_with_label("🔓 Unlock with Password")
        self.btn_auth_unlock.get_style_context().add_class("btn-unlock")
        self.btn_auth_unlock.set_tooltip_text("Enter Linux system password to reveal Secret Key")
        self.btn_auth_unlock.connect("clicked", self._on_unlock_clicked)
        locked_box.pack_end(self.btn_auth_unlock, False, False, 0)
        self.secret_stack.add_named(locked_box, "locked")

        # Unlocked page
        unlocked_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.entry_secret_key = Gtk.Entry()
        self.entry_secret_key.get_style_context().add_class("mono-entry")
        self.entry_secret_key.set_visibility(True)
        self.entry_secret_key.set_placeholder_text("Secret Access Key")
        self.entry_secret_key.set_hexpand(True)
        unlocked_box.pack_start(self.entry_secret_key, True, True, 0)

        self.btn_toggle_secret = Gtk.Button.new_from_icon_name("view-conceal-symbolic", Gtk.IconSize.BUTTON)
        self.btn_toggle_secret.set_tooltip_text("Toggle Show / Hide Secret Key")
        self.btn_toggle_secret.connect("clicked", lambda b: self._toggle_visibility(self.entry_secret_key, self.btn_toggle_secret))
        unlocked_box.pack_start(self.btn_toggle_secret, False, False, 0)

        btn_copy_secret = Gtk.Button.new_from_icon_name("edit-copy-symbolic", Gtk.IconSize.BUTTON)
        btn_copy_secret.set_tooltip_text("Copy Secret Access Key")
        btn_copy_secret.connect("clicked", lambda b: self._copy_entry(self.entry_secret_key, "Secret Access Key"))
        unlocked_box.pack_start(btn_copy_secret, False, False, 0)

        self.btn_lock_again = Gtk.Button.new_with_label("🔒 Lock")
        self.btn_lock_again.get_style_context().add_class("btn-lock")
        self.btn_lock_again.set_tooltip_text("Re-lock and hide secret key")
        self.btn_lock_again.connect("clicked", self._on_lock_clicked)
        unlocked_box.pack_start(self.btn_lock_again, False, False, 0)

        self.secret_stack.add_named(unlocked_box, "unlocked")
        grid_cred.attach(self.secret_stack, 1, 1, 1, 1)

        # Row 2: Session Token (Optional)
        lbl_token = Gtk.Label(label="Session Token:")
        lbl_token.set_halign(Gtk.Align.END)
        grid_cred.attach(lbl_token, 0, 2, 1, 1)

        token_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.entry_session_token = Gtk.Entry()
        self.entry_session_token.set_visibility(False)
        self.entry_session_token.get_style_context().add_class("mono-entry")
        self.entry_session_token.set_placeholder_text("Optional (for temporary STS credentials)")
        self.entry_session_token.set_hexpand(True)
        token_box.pack_start(self.entry_session_token, True, True, 0)

        btn_toggle_token = Gtk.Button.new_from_icon_name("view-reveal-symbolic", Gtk.IconSize.BUTTON)
        btn_toggle_token.set_tooltip_text("Toggle Show / Hide Session Token")
        btn_toggle_token.connect("clicked", lambda b: self._toggle_visibility(self.entry_session_token, btn_toggle_token))
        token_box.pack_start(btn_toggle_token, False, False, 0)

        grid_cred.attach(token_box, 1, 2, 1, 1)
        self.detail_container.pack_start(cred_card, False, False, 0)

        # 3. Card: Region & Output
        conf_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        conf_card.get_style_context().add_class("modern-card")

        hdr_conf = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        lbl_o_icon = Gtk.Image.new_from_icon_name("preferences-system-symbolic", Gtk.IconSize.BUTTON)
        hdr_conf.pack_start(lbl_o_icon, False, False, 0)
        lbl_o_title = Gtk.Label()
        lbl_o_title.set_markup("<b>Region &amp; Output Configuration</b>")
        lbl_o_title.get_style_context().add_class("card-header-title")
        hdr_conf.pack_start(lbl_o_title, False, False, 0)
        conf_card.pack_start(hdr_conf, False, False, 0)

        grid_conf = Gtk.Grid()
        grid_conf.set_row_spacing(12)
        grid_conf.set_column_spacing(14)
        conf_card.pack_start(grid_conf, False, False, 0)

        # Default Region
        lbl_region = Gtk.Label(label="Default Region:")
        lbl_region.set_halign(Gtk.Align.END)
        grid_conf.attach(lbl_region, 0, 0, 1, 1)

        self.combo_region = Gtk.ComboBoxText.new_with_entry()
        for r in STANDARD_REGIONS:
            self.combo_region.append_text(r)
        self.combo_region.set_hexpand(True)
        grid_conf.attach(self.combo_region, 1, 0, 1, 1)

        # Output Format
        lbl_output = Gtk.Label(label="Output Format:")
        lbl_output.set_halign(Gtk.Align.END)
        grid_conf.attach(lbl_output, 0, 1, 1, 1)

        self.combo_output = Gtk.ComboBoxText()
        for o in OUTPUT_FORMATS:
            self.combo_output.append_text(o)
        self.combo_output.set_hexpand(True)
        grid_conf.attach(self.combo_output, 1, 1, 1, 1)

        self.detail_container.pack_start(conf_card, False, False, 0)

        # 4. Terminal Quick-Connect Card
        snippet_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        snippet_card.get_style_context().add_class("modern-card")

        hdr_snip = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        lbl_snip_icon = Gtk.Image.new_from_icon_name("utilities-terminal-symbolic", Gtk.IconSize.BUTTON)
        hdr_snip.pack_start(lbl_snip_icon, False, False, 0)
        lbl_snip_title = Gtk.Label()
        lbl_snip_title.set_markup("<b>Quick Terminal Activation</b>")
        lbl_snip_title.get_style_context().add_class("card-header-title")
        hdr_snip.pack_start(lbl_snip_title, False, False, 0)
        snippet_card.pack_start(hdr_snip, False, False, 0)

        cli_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        cli_box.get_style_context().add_class("terminal-box")

        self.lbl_cli_export = Gtk.Label()
        self.lbl_cli_export.set_selectable(True)
        self.lbl_cli_export.set_halign(Gtk.Align.START)
        cli_box.pack_start(self.lbl_cli_export, True, True, 0)

        btn_copy_cli = Gtk.Button.new_from_icon_name("edit-copy-symbolic", Gtk.IconSize.BUTTON)
        btn_copy_cli.set_tooltip_text("Copy export command to clipboard")
        btn_copy_cli.connect("clicked", self._on_copy_export_clicked)
        cli_box.pack_end(btn_copy_cli, False, False, 0)

        snippet_card.pack_start(cli_box, False, False, 0)
        self.detail_container.pack_start(snippet_card, False, False, 0)

        # 5. Save & Reset Action Bar
        actions_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        actions_box.set_halign(Gtk.Align.END)
        actions_box.set_margin_top(4)

        self.btn_reset = Gtk.Button.new_with_label("Discard Changes")
        self.btn_reset.connect("clicked", lambda b: self._display_profile(self.selected_profile_name))
        actions_box.pack_start(self.btn_reset, False, False, 0)

        self.btn_save = Gtk.Button.new_with_label("Save Profile Changes")
        self.btn_save.get_style_context().add_class("suggested-action")
        self.btn_save.set_tooltip_text("Save updates to ~/.aws credentials and config (Ctrl+S)")
        self.btn_save.connect("clicked", self._on_save_clicked)
        actions_box.pack_start(self.btn_save, False, False, 0)

        self.detail_container.pack_start(actions_box, False, False, 4)

    def _toggle_visibility(self, entry: Gtk.Entry, button: Gtk.Button):
        current = entry.get_visibility()
        entry.set_visibility(not current)
        icon_name = "view-conceal-symbolic" if not current else "view-reveal-symbolic"
        button.set_image(Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON))

    def _copy_entry(self, entry: Gtk.Entry, label: str):
        val = entry.get_text().strip()
        if val:
            copy_to_clipboard(val)
            self.show_notification(f"{label} copied to clipboard!", Gtk.MessageType.INFO)
        else:
            self.show_notification(f"No {label} to copy.", Gtk.MessageType.WARNING)

    def _on_copy_export_clicked(self, button):
        if self.selected_profile_name:
            cmd = f"export AWS_PROFILE={self.selected_profile_name}"
            copy_to_clipboard(cmd)
            self.show_notification(f"Copied '{cmd}' to clipboard.", Gtk.MessageType.INFO)

    def show_notification(self, message: str, msg_type: Gtk.MessageType = Gtk.MessageType.INFO):
        self.info_bar.set_message_type(msg_type)
        self.info_bar_label.set_text(message)
        self.info_bar.show()

    def reload_profiles(self, select_name: Optional[str] = None):
        """Reloads all profiles from files and populates sidebar list."""
        self.profiles = self.mgr.get_profiles()

        # Clear existing rows
        for child in self.profile_listbox.get_children():
            self.profile_listbox.remove(child)

        names = sorted(self.profiles.keys(), key=lambda x: (x.lower() != "default", x.lower()))
        target_row = None

        for name in names:
            data = self.profiles[name]
            row = Gtk.ListBoxRow()
            row.profile_name = name
            row.profile_data = data
            row.get_style_context().add_class("sidebar-row")

            row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

            # Avatar Circle with Initials
            lbl_av = Gtk.Label(label=get_profile_initials(name))
            lbl_av.get_style_context().add_class("avatar-badge")
            lbl_av.get_style_context().add_class(f"avatar-{get_profile_color_index(name)}")
            row_box.pack_start(lbl_av, False, False, 0)

            # Center text box: Name & Details
            text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)

            top_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            lbl_name = Gtk.Label()
            lbl_name.set_markup(f"<b>{GLib.markup_escape_text(name)}</b>")
            lbl_name.set_halign(Gtk.Align.START)
            top_box.pack_start(lbl_name, True, True, 0)

            if name.lower() == "default":
                lbl_default = Gtk.Label(label="DEFAULT")
                lbl_default.get_style_context().add_class("badge-default")
                top_box.pack_end(lbl_default, False, False, 0)

            text_box.pack_start(top_box, False, False, 0)

            bottom_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            region_str = data.get("region", "").strip() or "No Region"
            lbl_reg = Gtk.Label(label=region_str)
            lbl_reg.get_style_context().add_class("badge-region")
            bottom_box.pack_start(lbl_reg, False, False, 0)

            # Lock status tag in row
            is_unlocked = name in self.unlocked_profiles
            lbl_lock = Gtk.Label(label="🔓" if is_unlocked else "🔒")
            lbl_lock.get_style_context().add_class("dim-label")
            bottom_box.pack_end(lbl_lock, False, False, 0)

            text_box.pack_start(bottom_box, False, False, 0)
            row_box.pack_start(text_box, True, True, 0)

            row.add(row_box)
            row.show_all()
            self.profile_listbox.add(row)

            if select_name and name == select_name:
                target_row = row
            elif not target_row and not select_name and self.selected_profile_name == name:
                target_row = row

        count = len(names)
        self.lbl_count.set_text(f"{count} configured account{'s' if count != 1 else ''}")

        if target_row:
            self.profile_listbox.select_row(target_row)
        elif names:
            first_row = self.profile_listbox.get_row_at_index(0)
            self.profile_listbox.select_row(first_row)
        else:
            self.selected_profile_name = None
            self.detail_stack.set_visible_child_name("empty")

    def _list_filter_func(self, row: Gtk.ListBoxRow) -> bool:
        search_query = self.search_entry.get_text().strip().lower()
        if not search_query:
            return True
        name = row.profile_name.lower()
        region = row.profile_data.get("region", "").lower()
        key = row.profile_data.get("aws_access_key_id", "").lower()
        return search_query in name or search_query in region or search_query in key

    def _on_search_changed(self, entry):
        self.profile_listbox.invalidate_filter()

    def _on_row_selected(self, listbox, row):
        if row is None:
            return
        self._display_profile(row.profile_name)

    def _display_profile(self, name: Optional[str]):
        if not name or name not in self.profiles:
            self.selected_profile_name = None
            self.detail_stack.set_visible_child_name("empty")
            return

        self.selected_profile_name = name
        data = self.profiles[name]

        # Reset test connection box
        self.test_status_box.hide()
        self.test_status_spinner.stop()

        # Update Hero avatar
        for i in range(8):
            self.lbl_hero_avatar.get_style_context().remove_class(f"avatar-{i}")
        self.lbl_hero_avatar.set_text(get_profile_initials(name))
        self.lbl_hero_avatar.get_style_context().add_class("hero-avatar")
        self.lbl_hero_avatar.get_style_context().add_class(f"avatar-{get_profile_color_index(name)}")

        self.lbl_profile_hero.set_markup(f"<b>{GLib.markup_escape_text(name)}</b>")
        reg_text = data.get("region", "").strip() or "No region configured"
        fmt_text = data.get("output", "json")
        self.lbl_hero_sub.set_markup(f"Region: <b>{GLib.markup_escape_text(reg_text)}</b> • Output: <b>{GLib.markup_escape_text(fmt_text)}</b>")

        # Credentials
        self.entry_access_key.set_text(data.get("aws_access_key_id", ""))
        self.entry_secret_key.set_text(data.get("aws_secret_access_key", ""))
        self.entry_session_token.set_text(data.get("aws_session_token", ""))

        # Check lock status
        self._update_secret_lock_view()

        # Region
        curr_region = data.get("region", "")
        self.combo_region.get_child().set_text(curr_region)

        # Output
        curr_output = data.get("output", "json")
        try:
            idx = OUTPUT_FORMATS.index(curr_output)
            self.combo_output.set_active(idx)
        except ValueError:
            self.combo_output.set_active(0)

        # CLI snippet
        self.lbl_cli_export.set_text(f"export AWS_PROFILE={name}")

        self.detail_stack.set_visible_child_name("detail")

    def _update_secret_lock_view(self):
        name = self.selected_profile_name
        is_unlocked = bool(name and name in self.unlocked_profiles)

        if is_unlocked:
            curr_data = self.profiles.get(name, {})
            secret = curr_data.get("aws_secret_access_key", "")
            self.entry_secret_key.set_text(secret)
            self.entry_secret_key.set_visibility(True)
            self.btn_toggle_secret.set_image(Gtk.Image.new_from_icon_name("view-conceal-symbolic", Gtk.IconSize.BUTTON))
            self.secret_stack.set_visible_child_name("unlocked")
            self.lbl_lock_status.set_text("UNLOCKED")
            self.lbl_lock_status.get_style_context().remove_class("badge-locked")
            self.lbl_lock_status.get_style_context().add_class("badge-unlocked")
        else:
            self.secret_stack.set_visible_child_name("locked")
            self.lbl_lock_status.set_text("LOCKED")
            self.lbl_lock_status.get_style_context().remove_class("badge-unlocked")
            self.lbl_lock_status.get_style_context().add_class("badge-locked")

    def _on_unlock_clicked(self, button):
        if not self.selected_profile_name:
            return

        dialog = SystemAuthDialog(self, self.selected_profile_name)
        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.OK:
            self.unlocked_profiles.add(self.selected_profile_name)
            self._update_secret_lock_view()
            self.show_notification("Secret credentials unlocked successfully.", Gtk.MessageType.INFO)
            # Update sidebar indicator
            self.reload_profiles(select_name=self.selected_profile_name)

    def _on_lock_clicked(self, button):
        if self.selected_profile_name:
            self.unlocked_profiles.discard(self.selected_profile_name)
            self._update_secret_lock_view()
            self.show_notification("Secret credentials locked.", Gtk.MessageType.INFO)
            self.reload_profiles(select_name=self.selected_profile_name)

    def _on_save_clicked(self, button):
        if not self.selected_profile_name:
            return

        name = self.selected_profile_name
        access_key = self.entry_access_key.get_text().strip()
        region = self.combo_region.get_child().get_text().strip()
        output_format = self.combo_output.get_active_text() or "json"
        session_token = self.entry_session_token.get_text().strip()

        # If secret is unlocked, take from entry; otherwise preserve existing secret
        curr_data = self.profiles.get(name, {})
        if name in self.unlocked_profiles:
            secret_key = self.entry_secret_key.get_text().strip()
        else:
            secret_key = curr_data.get("aws_secret_access_key", "")

        try:
            self.mgr.save_profile(
                name=name,
                access_key=access_key,
                secret_key=secret_key,
                region=region,
                output_format=output_format,
                session_token=session_token,
                extra_cred=curr_data.get("extra_cred"),
                extra_conf=curr_data.get("extra_conf"),
            )
            self.show_notification(f"Profile '{name}' updated successfully.", Gtk.MessageType.INFO)
            self.reload_profiles(select_name=name)
        except Exception as e:
            self.show_notification(f"Error saving profile: {e}", Gtk.MessageType.ERROR)

    def _on_add_profile_clicked(self, button):
        dialog = AddProfileDialog(self)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            name, access_key, secret_key, region, output_fmt, session_token = dialog.get_values()
            try:
                self.mgr.save_profile(
                    name=name,
                    access_key=access_key,
                    secret_key=secret_key,
                    region=region,
                    output_format=output_fmt,
                    session_token=session_token,
                )
                # Newly created profile is unlocked for this session
                self.unlocked_profiles.add(name)
                self.show_notification(f"Profile '{name}' created successfully!", Gtk.MessageType.INFO)
                self.reload_profiles(select_name=name)
            except Exception as e:
                self.show_notification(f"Failed to create profile: {e}", Gtk.MessageType.ERROR)
        dialog.destroy()

    def _on_rename_clicked(self, button):
        if not self.selected_profile_name:
            return

        current_name = self.selected_profile_name
        dialog = RenameProfileDialog(self, current_name)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            new_name = dialog.get_new_name()
            try:
                self.mgr.rename_profile(current_name, new_name)
                if current_name in self.unlocked_profiles:
                    self.unlocked_profiles.remove(current_name)
                    self.unlocked_profiles.add(new_name)
                self.show_notification(f"Renamed '{current_name}' to '{new_name}'.", Gtk.MessageType.INFO)
                self.reload_profiles(select_name=new_name)
            except Exception as e:
                self.show_notification(f"Rename failed: {e}", Gtk.MessageType.ERROR)
        dialog.destroy()

    def _on_delete_clicked(self, button):
        if not self.selected_profile_name:
            return

        name = self.selected_profile_name
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=Gtk.DialogFlags.MODAL,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.NONE,
            text=f"Delete profile '{name}'?",
        )
        dialog.format_secondary_text(
            f"This will permanently delete profile '{name}' and its credentials from "
            "~/.aws/credentials and ~/.aws/config.\n(A backup will be created automatically in ~/.aws/backups)."
        )
        dialog.add_button("_Cancel", Gtk.ResponseType.CANCEL)
        btn_del = dialog.add_button("_Delete Profile", Gtk.ResponseType.OK)
        btn_del.get_style_context().add_class("destructive-action")

        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.OK:
            try:
                self.mgr.delete_profile(name)
                self.unlocked_profiles.discard(name)
                self.show_notification(f"Profile '{name}' was deleted.", Gtk.MessageType.INFO)
                self.reload_profiles()
            except Exception as e:
                self.show_notification(f"Delete failed: {e}", Gtk.MessageType.ERROR)

    def _on_test_connection_clicked(self, button):
        if not self.selected_profile_name:
            return

        name = self.selected_profile_name
        self.btn_test.set_sensitive(False)

        # Show status box with spinner
        for c in ["test-success-box", "test-error-box"]:
            self.test_status_box.get_style_context().remove_class(c)
        self.test_status_box.get_style_context().add_class("test-loading-box")
        self.test_status_icon.hide()
        self.test_status_spinner.show()
        self.test_status_spinner.start()
        self.test_status_label.set_markup(f"<b>Contacting AWS STS...</b>\n<small>Testing credentials for '<b>{name}</b>'</small>")
        self.test_status_label.show()
        self.test_status_box.show_all()
        self.test_status_icon.hide()

        def run_test():
            success, data, error_msg = self.mgr.test_profile(name)
            GLib.idle_add(self._on_test_finished, success, data, error_msg)

        threading.Thread(target=run_test, daemon=True).start()

    def _on_test_finished(self, success: bool, data: Dict[str, Any], error_msg: str):
        self.btn_test.set_sensitive(True)
        self.test_status_spinner.stop()
        self.test_status_spinner.hide()
        self.test_status_box.get_style_context().remove_class("test-loading-box")

        if success:
            self.test_status_box.get_style_context().add_class("test-success-box")
            self.test_status_icon.set_from_icon_name("emblem-default-symbolic", Gtk.IconSize.BUTTON)
            self.test_status_icon.show()
            acc = data.get("Account", "Unknown")
            arn = data.get("Arn", "Unknown")
            user_id = data.get("UserId", "Unknown")
            text = (
                f"<b>AWS Connection Verified Successfully!</b>\n"
                f"• <b>Account ID:</b> {GLib.markup_escape_text(acc)}\n"
                f"• <b>ARN:</b> {GLib.markup_escape_text(arn)}\n"
                f"• <b>UserId:</b> {GLib.markup_escape_text(user_id)}"
            )
            self.test_status_label.set_markup(text)
            self.test_status_label.show()
        else:
            self.test_status_box.get_style_context().add_class("test-error-box")
            self.test_status_icon.set_from_icon_name("dialog-error-symbolic", Gtk.IconSize.BUTTON)
            self.test_status_icon.show()
            escaped_err = GLib.markup_escape_text(error_msg or "Unknown error")
            text = f"<b>AWS Connection Failed:</b>\n<small>{escaped_err}</small>"
            self.test_status_label.set_markup(text)
            self.test_status_label.show()

        self.test_status_box.show()

    def _on_key_press(self, widget, event):
        keyval = event.keyval
        ctrl = bool(event.state & Gdk.ModifierType.CONTROL_MASK)

        if ctrl and keyval in (Gdk.KEY_n, Gdk.KEY_N):
            self._on_add_profile_clicked(None)
            return True
        elif ctrl and keyval in (Gdk.KEY_r, Gdk.KEY_R):
            self.reload_profiles()
            return True
        elif ctrl and keyval in (Gdk.KEY_s, Gdk.KEY_S):
            self._on_save_clicked(None)
            return True
        elif keyval == Gdk.KEY_F2:
            self._on_rename_clicked(None)
            return True
        elif ctrl and keyval in (Gdk.KEY_d, Gdk.KEY_D):
            self._on_delete_clicked(None)
            return True
        return False


class AddProfileDialog(Gtk.Dialog):
    def __init__(self, parent):
        super().__init__(
            title="Create New AWS Profile",
            transient_for=parent,
            flags=Gtk.DialogFlags.MODAL,
        )
        self.set_default_size(460, 400)
        self.add_button("_Cancel", Gtk.ResponseType.CANCEL)
        self.btn_create = self.add_button("_Create Profile", Gtk.ResponseType.OK)
        self.btn_create.get_style_context().add_class("suggested-action")
        self.btn_create.set_sensitive(False)

        content = self.get_content_area()
        content.set_margin_start(20)
        content.set_margin_end(20)
        content.set_margin_top(16)
        content.set_margin_bottom(16)
        content.set_spacing(14)

        lbl_desc = Gtk.Label()
        lbl_desc.set_markup("<b><big>Configure New AWS Account</big></b>")
        lbl_desc.set_halign(Gtk.Align.START)
        content.pack_start(lbl_desc, False, False, 0)

        grid = Gtk.Grid()
        grid.set_row_spacing(12)
        grid.set_column_spacing(14)
        content.pack_start(grid, True, True, 0)

        # Profile Name
        lbl_n = Gtk.Label(label="Profile Name*:")
        lbl_n.set_halign(Gtk.Align.END)
        grid.attach(lbl_n, 0, 0, 1, 1)

        self.entry_name = Gtk.Entry()
        self.entry_name.set_placeholder_text("e.g. dev, prod, personal")
        self.entry_name.set_hexpand(True)
        self.entry_name.connect("changed", self._validate)
        grid.attach(self.entry_name, 1, 0, 1, 1)

        # Access Key
        lbl_k = Gtk.Label(label="Access Key ID:")
        lbl_k.set_halign(Gtk.Align.END)
        grid.attach(lbl_k, 0, 1, 1, 1)

        self.entry_key = Gtk.Entry()
        self.entry_key.get_style_context().add_class("mono-entry")
        self.entry_key.set_placeholder_text("AKIA...")
        grid.attach(self.entry_key, 1, 1, 1, 1)

        # Secret Key
        lbl_s = Gtk.Label(label="Secret Access Key:")
        lbl_s.set_halign(Gtk.Align.END)
        grid.attach(lbl_s, 0, 2, 1, 1)

        self.entry_secret = Gtk.Entry()
        self.entry_secret.get_style_context().add_class("mono-entry")
        self.entry_secret.set_visibility(False)
        self.entry_secret.set_placeholder_text("Secret Key")
        grid.attach(self.entry_secret, 1, 2, 1, 1)

        # Region
        lbl_r = Gtk.Label(label="Default Region:")
        lbl_r.set_halign(Gtk.Align.END)
        grid.attach(lbl_r, 0, 3, 1, 1)

        self.combo_region = Gtk.ComboBoxText.new_with_entry()
        for r in STANDARD_REGIONS:
            self.combo_region.append_text(r)
        self.combo_region.get_child().set_text("us-east-1")
        grid.attach(self.combo_region, 1, 3, 1, 1)

        # Output
        lbl_o = Gtk.Label(label="Output Format:")
        lbl_o.set_halign(Gtk.Align.END)
        grid.attach(lbl_o, 0, 4, 1, 1)

        self.combo_output = Gtk.ComboBoxText()
        for o in OUTPUT_FORMATS:
            self.combo_output.append_text(o)
        self.combo_output.set_active(0)
        grid.attach(self.combo_output, 1, 4, 1, 1)

        # Session Token
        lbl_t = Gtk.Label(label="Session Token:")
        lbl_t.set_halign(Gtk.Align.END)
        grid.attach(lbl_t, 0, 5, 1, 1)

        self.entry_token = Gtk.Entry()
        self.entry_token.get_style_context().add_class("mono-entry")
        self.entry_token.set_visibility(False)
        self.entry_token.set_placeholder_text("Optional")
        grid.attach(self.entry_token, 1, 5, 1, 1)

        self.show_all()

    def _validate(self, entry):
        val = entry.get_text().strip()
        valid = bool(val and " " not in val and "/" not in val and "\\" not in val)
        self.btn_create.set_sensitive(valid)

    def get_values(self):
        return (
            self.entry_name.get_text().strip(),
            self.entry_key.get_text().strip(),
            self.entry_secret.get_text().strip(),
            self.combo_region.get_child().get_text().strip(),
            self.combo_output.get_active_text() or "json",
            self.entry_token.get_text().strip(),
        )


class RenameProfileDialog(Gtk.Dialog):
    def __init__(self, parent, current_name: str):
        super().__init__(
            title="Rename Profile",
            transient_for=parent,
            flags=Gtk.DialogFlags.MODAL,
        )
        self.current_name = current_name
        self.set_default_size(380, 160)
        self.add_button("_Cancel", Gtk.ResponseType.CANCEL)
        self.btn_rename = self.add_button("_Rename", Gtk.ResponseType.OK)
        self.btn_rename.get_style_context().add_class("suggested-action")
        self.btn_rename.set_sensitive(False)

        content = self.get_content_area()
        content.set_margin_start(18)
        content.set_margin_end(18)
        content.set_margin_top(16)
        content.set_margin_bottom(16)
        content.set_spacing(12)

        lbl = Gtk.Label()
        lbl.set_markup(f"Rename profile <b>{GLib.markup_escape_text(current_name)}</b> to:")
        lbl.set_halign(Gtk.Align.START)
        content.pack_start(lbl, False, False, 0)

        self.entry_new = Gtk.Entry()
        self.entry_new.set_text(current_name)
        self.entry_new.connect("changed", self._validate)
        content.pack_start(self.entry_new, False, False, 0)

        self.show_all()

    def _validate(self, entry):
        val = entry.get_text().strip()
        valid = bool(val and val != self.current_name and " " not in val and "/" not in val)
        self.btn_rename.set_sensitive(valid)

    def get_new_name(self):
        return self.entry_new.get_text().strip()
