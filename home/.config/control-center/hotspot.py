#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, GLib, Gtk  # noqa: E402

from common.async_worker import AsyncWorker  # noqa: E402
from common.widgets import (  # noqa: E402
    BottomActionButton,
    BusyOverlay,
    ControlHeader,
    SectionLabel,
)
from common.window import BaseControlWindow  # noqa: E402
from services.hotspot import HotspotError, HotspotInfo, HotspotService  # noqa: E402


APP_ID = "io.github.moss.ControlCenter.Hotspot"
BASE_DIR = Path(__file__).resolve().parent
CSS_FILE = BASE_DIR / "common" / "style.css"


class HotspotWindow(BaseControlWindow):
    def __init__(self, application: Adw.Application) -> None:
        super().__init__(application, width=400, height=570)
        self.set_title("Hotspot")
        self.load_css(CSS_FILE)

        self.service = HotspotService()
        self.worker = AsyncWorker()
        self.info = HotspotInfo(
            enabled=False,
            profile_name=self.service.PROFILE_NAME,
            ssid=self.service.DEFAULT_SSID,
            password="",
            interface="",
            clients=(),
        )
        self.operation_running = False
        self.password_visible = False
        self.refresh_source_id: int | None = None

        self.main_header = ControlHeader(
            title="Hotspot",
            icon="󰖩",
            left_icon="",
            on_left_clicked=self._toggle_hotspot,
            on_close_clicked=lambda _button: self.close(),
        )
        self.main_header.set_left_tooltip("Turn hotspot on")

        self.root.append(self.stack)
        self._build_main_page()
        self._build_confirmation_page()
        self._build_edit_page()
        self.show_page("main")

        self.connect("close-request", self._on_close_request)
        self._refresh()
        self.refresh_source_id = GLib.timeout_add_seconds(5, self._periodic_refresh)

    def _build_main_page(self) -> None:
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        page.append(self.main_header)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        content.set_margin_top(15)
        content.set_margin_bottom(15)
        content.set_margin_start(15)
        content.set_margin_end(15)
        content.set_vexpand(True)
        page.append(content)

        self.main_body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        self.main_body.set_vexpand(True)
        content.append(self.main_body)

        self.main_body.append(SectionLabel("Hotspot details"))

        details_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        details_card.add_css_class("details-card")

        ssid_row = Gtk.Button()
        ssid_row.add_css_class("flat-info-row")
        ssid_row.connect("clicked", self._open_edit_page)
        ssid_content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        ssid_text = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        ssid_text.set_hexpand(True)
        ssid_label = Gtk.Label(label="Network name", xalign=0)
        ssid_label.add_css_class("connected-strength")
        self.ssid_value = Gtk.Label(label="", xalign=0)
        self.ssid_value.add_css_class("network-name")
        ssid_text.append(ssid_label)
        ssid_text.append(self.ssid_value)
        ssid_content.append(ssid_text)
        ssid_arrow = Gtk.Label(label="")
        ssid_arrow.add_css_class("nerd-icon")
        ssid_arrow.add_css_class("network-arrow")
        ssid_content.append(ssid_arrow)
        ssid_row.set_child(ssid_content)
        details_card.append(ssid_row)

        separator = Gtk.Separator()
        details_card.append(separator)

        password_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        password_row.add_css_class("info-row")

        password_text = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        password_text.set_hexpand(True)
        password_label = Gtk.Label(label="Password", xalign=0)
        password_label.add_css_class("connected-strength")
        self.password_value = Gtk.Label(label="", xalign=0)
        self.password_value.add_css_class("network-name")
        password_text.append(password_label)
        password_text.append(self.password_value)
        password_row.append(password_text)

        self.reveal_password_button = Gtk.Button(label="")
        self.reveal_password_button.add_css_class("header-button")
        self.reveal_password_button.add_css_class("nerd-icon")
        self.reveal_password_button.set_tooltip_text("Show password")
        self.reveal_password_button.connect(
            "clicked",
            self._toggle_password_reveal,
        )
        password_row.append(self.reveal_password_button)

        edit_button = Gtk.Button(label="")
        edit_button.add_css_class("header-button")
        edit_button.add_css_class("nerd-icon")
        edit_button.set_tooltip_text("Edit hotspot")
        edit_button.connect("clicked", self._open_edit_page)
        password_row.append(edit_button)

        details_card.append(password_row)
        self.main_body.append(details_card)

        self.main_body.append(SectionLabel("Connected devices"))

        clients_frame = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        clients_frame.add_css_class("network-list-frame")
        clients_frame.set_vexpand(True)

        self.clients_list = Gtk.ListBox()
        self.clients_list.set_selection_mode(Gtk.SelectionMode.NONE)

        self.clients_empty = Gtk.Label(label="No connected devices.")
        self.clients_empty.set_wrap(True)
        self.clients_empty.set_margin_top(26)
        self.clients_empty.set_margin_bottom(26)
        self.clients_empty.add_css_class("empty-state")
        self.clients_list.set_placeholder(self.clients_empty)

        clients_scroller = Gtk.ScrolledWindow()
        clients_scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        clients_scroller.set_vexpand(True)
        clients_scroller.set_child(self.clients_list)
        clients_frame.append(clients_scroller)
        self.main_body.append(clients_frame)

        self.settings_button = BottomActionButton("Open Network Settings")
        self.settings_button.connect("clicked", self._open_settings)
        self.main_body.append(self.settings_button)

        self.main_busy = BusyOverlay()
        content.append(self.main_busy)

        self.stack.add_named(page, "main")

    def _build_confirmation_page(self) -> None:
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.confirm_header = ControlHeader(
            title="Start Hotspot",
            icon="󰖩",
            left_icon="",
            on_left_clicked=self._back_to_main,
            on_close_clicked=lambda _button: self.close(),
        )
        self.confirm_header.set_left_tooltip("Back")
        page.append(self.confirm_header)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content.set_margin_top(30)
        content.set_margin_bottom(18)
        content.set_margin_start(22)
        content.set_margin_end(22)
        content.set_vexpand(True)

        icon = Gtk.Label(label="󰖩")
        icon.add_css_class("nerd-icon")
        icon.add_css_class("pair-device-icon")
        content.append(icon)

        title = Gtk.Label(label="Disconnect from Wi-Fi?")
        title.add_css_class("password-network")
        content.append(title)

        message = Gtk.Label(
            label=(
                "Starting the hotspot will disconnect the current Wi-Fi "
                "connection and use the wireless adapter as an access point."
            )
        )
        message.set_wrap(True)
        message.set_justify(Gtk.Justification.CENTER)
        message.add_css_class("connected-strength")
        content.append(message)

        self.confirm_error = Gtk.Label(label="")
        self.confirm_error.set_wrap(True)
        self.confirm_error.set_justify(Gtk.Justification.CENTER)
        self.confirm_error.add_css_class("error-label")
        self.confirm_error.set_visible(False)
        content.append(self.confirm_error)

        spacer = Gtk.Box()
        spacer.set_vexpand(True)
        content.append(spacer)

        actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        actions.set_homogeneous(True)

        self.cancel_start_button = Gtk.Button(label="Cancel")
        self.cancel_start_button.add_css_class("secondary-action")
        self.cancel_start_button.connect("clicked", self._back_to_main)
        actions.append(self.cancel_start_button)

        self.continue_start_button = Gtk.Button(label="Continue")
        self.continue_start_button.add_css_class("suggested-action")
        self.continue_start_button.add_css_class("connect-button")
        self.continue_start_button.connect("clicked", self._start_hotspot)
        actions.append(self.continue_start_button)

        content.append(actions)

        self.confirm_busy = BusyOverlay()
        content.append(self.confirm_busy)

        page.append(content)
        self.stack.add_named(page, "confirm")

    def _build_edit_page(self) -> None:
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.edit_header = ControlHeader(
            title="Edit Hotspot",
            icon="󰖩",
            left_icon="",
            on_left_clicked=self._back_to_main,
            on_close_clicked=lambda _button: self.close(),
        )
        self.edit_header.set_left_tooltip("Back")
        page.append(self.edit_header)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        content.set_margin_top(22)
        content.set_margin_bottom(18)
        content.set_margin_start(18)
        content.set_margin_end(18)
        content.set_vexpand(True)

        content.append(SectionLabel("Network name"))
        self.ssid_entry = Gtk.Entry()
        self.ssid_entry.set_hexpand(True)
        content.append(self.ssid_entry)

        content.append(SectionLabel("Password"))
        self.password_entry = Gtk.Entry()
        self.password_entry.set_visibility(False)
        self.password_entry.set_input_purpose(Gtk.InputPurpose.PASSWORD)
        self.password_entry.set_hexpand(True)
        content.append(self.password_entry)

        self.show_edit_password = Gtk.CheckButton(label="Show password")
        self.show_edit_password.connect(
            "toggled",
            lambda button: self.password_entry.set_visibility(
                button.get_active()
            ),
        )
        content.append(self.show_edit_password)

        hint = Gtk.Label(
            label="Use 8–63 characters for WPA security.",
            xalign=0,
        )
        hint.add_css_class("connected-strength")
        content.append(hint)

        self.edit_error = Gtk.Label(label="", xalign=0)
        self.edit_error.set_wrap(True)
        self.edit_error.add_css_class("error-label")
        self.edit_error.set_visible(False)
        content.append(self.edit_error)

        spacer = Gtk.Box()
        spacer.set_vexpand(True)
        content.append(spacer)

        self.save_button = Gtk.Button(label="Save")
        self.save_button.add_css_class("suggested-action")
        self.save_button.add_css_class("connect-button")
        self.save_button.connect("clicked", self._save_hotspot)
        content.append(self.save_button)

        self.edit_busy = BusyOverlay()
        content.append(self.edit_busy)

        page.append(content)
        self.stack.add_named(page, "edit")

    def _refresh(self) -> None:
        if self.operation_running:
            return
        self.worker.submit(
            self.service.get_info,
            self._info_loaded,
            self._background_error,
        )

    def _info_loaded(self, info: HotspotInfo) -> None:
        self.info = info
        self._render_info()

    def _render_info(self) -> None:
        enabled = self.info.enabled
        self.main_header.set_left_icon("" if enabled else "")
        self.main_header.set_left_tooltip(
            "Turn hotspot off" if enabled else "Turn hotspot on"
        )
        self.main_body.set_visible(enabled)

        self.ssid_value.set_label(self.info.ssid)
        self._render_password()
        self._render_clients()

    def _render_password(self) -> None:
        password = self.info.password or "Unavailable"
        if self.password_visible or password == "Unavailable":
            shown = password
        else:
            shown = "•" * min(max(len(password), 8), 14)
        self.password_value.set_label(shown)
        self.reveal_password_button.set_label(
            "" if self.password_visible else ""
        )
        self.reveal_password_button.set_tooltip_text(
            "Hide password" if self.password_visible else "Show password"
        )

    def _render_clients(self) -> None:
        while child := self.clients_list.get_first_child():
            self.clients_list.remove(child)

        count = len(self.info.clients)
        self.clients_empty.set_label(
            "No connected devices."
            if count == 0
            else f"{count} connected device{'s' if count != 1 else ''}."
        )

        for client in self.info.clients:
            row = Gtk.ListBoxRow()
            row.set_activatable(False)
            row.add_css_class("network-row")

            content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            content.set_margin_top(11)
            content.set_margin_bottom(11)
            content.set_margin_start(13)
            content.set_margin_end(13)

            icon = Gtk.Label(label="󰌘")
            icon.add_css_class("nerd-icon")
            icon.add_css_class("network-icon")
            content.append(icon)

            text = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            text.set_hexpand(True)
            ip = Gtk.Label(label=client.ip, xalign=0)
            ip.add_css_class("network-name")
            mac = Gtk.Label(label=client.mac, xalign=0)
            mac.add_css_class("connected-strength")
            text.append(ip)
            text.append(mac)
            content.append(text)

            row.set_child(content)
            self.clients_list.append(row)

    def _toggle_hotspot(self, _button: Gtk.Button) -> None:
        if self.operation_running:
            return
        if self.info.enabled:
            self._stop_hotspot()
            return

        self.operation_running = True
        self.main_header.set_left_sensitive(False)
        self.main_busy.show_busy("Checking Wi-Fi connection…")
        self.worker.submit(
            self.service.wifi_client_connected,
            self._client_state_loaded,
            self._enable_check_failed,
        )

    def _client_state_loaded(self, connected: bool) -> None:
        self.operation_running = False
        self.main_header.set_left_sensitive(True)
        self.main_busy.hide_busy()

        if connected:
            self.confirm_error.set_visible(False)
            self.show_page("confirm")
        else:
            self._start_hotspot(None)

    def _enable_check_failed(self, error: Exception) -> None:
        self.operation_running = False
        self.main_header.set_left_sensitive(True)
        self.main_busy.hide_busy()
        self._show_main_error(str(error))

    def _start_hotspot(self, _button: Gtk.Button | None) -> None:
        if self.operation_running:
            return

        self.operation_running = True
        on_confirm = self.stack.get_visible_child_name() == "confirm"

        if on_confirm:
            self.confirm_header.set_left_sensitive(False)
            self.cancel_start_button.set_sensitive(False)
            self.continue_start_button.set_sensitive(False)
            self.confirm_error.set_visible(False)
            self.confirm_busy.show_busy("Starting hotspot…")
        else:
            self.main_header.set_left_sensitive(False)
            self.main_busy.show_busy("Starting hotspot…")

        self.worker.submit(
            self.service.enable,
            self._hotspot_started,
            lambda error: self._hotspot_start_failed(error, on_confirm),
        )

    def _hotspot_started(self, info: HotspotInfo) -> None:
        self.operation_running = False
        self._restore_start_controls()
        self.info = info
        self.password_visible = False
        self._render_info()
        self.show_page("main")
        self.service.notify(
            "Hotspot started",
            f"{info.ssid} is ready for connections.",
        )

    def _hotspot_start_failed(
        self,
        error: Exception,
        on_confirm: bool,
    ) -> None:
        self.operation_running = False
        self._restore_start_controls()
        message = str(error).strip() or "Could not start the hotspot."
        if on_confirm:
            self.confirm_error.set_label(message)
            self.confirm_error.set_visible(True)
        else:
            self._show_main_error(message)

    def _restore_start_controls(self) -> None:
        self.main_header.set_left_sensitive(True)
        self.main_busy.hide_busy()
        self.confirm_header.set_left_sensitive(True)
        self.cancel_start_button.set_sensitive(True)
        self.continue_start_button.set_sensitive(True)
        self.confirm_busy.hide_busy()

    def _stop_hotspot(self) -> None:
        self.operation_running = True
        self.main_header.set_left_sensitive(False)
        self.main_body.set_sensitive(False)
        self.main_busy.show_busy("Stopping hotspot…")

        self.worker.submit(
            self.service.disable,
            self._hotspot_stopped,
            self._hotspot_stop_failed,
        )

    def _hotspot_stopped(self, info: HotspotInfo) -> None:
        self.operation_running = False
        self.main_header.set_left_sensitive(True)
        self.main_body.set_sensitive(True)
        self.main_busy.hide_busy()
        self.info = info
        self._render_info()
        self.service.notify("Hotspot stopped", "The hotspot is now off.")

    def _hotspot_stop_failed(self, error: Exception) -> None:
        self.operation_running = False
        self.main_header.set_left_sensitive(True)
        self.main_body.set_sensitive(True)
        self.main_busy.hide_busy()
        self._show_main_error(str(error))

    def _toggle_password_reveal(self, _button: Gtk.Button) -> None:
        self.password_visible = not self.password_visible
        self._render_password()

    def _open_edit_page(self, _button: Gtk.Button) -> None:
        if self.operation_running:
            return
        self.ssid_entry.set_text(self.info.ssid)
        self.password_entry.set_text(self.info.password)
        self.password_entry.set_visibility(False)
        self.show_edit_password.set_active(False)
        self.edit_error.set_visible(False)
        self.save_button.set_sensitive(True)
        self.edit_header.set_left_sensitive(True)
        self.edit_busy.hide_busy()
        self.show_page("edit")
        GLib.idle_add(self.ssid_entry.grab_focus)

    def _save_hotspot(self, _button: Gtk.Button) -> None:
        if self.operation_running:
            return

        ssid = self.ssid_entry.get_text().strip()
        password = self.password_entry.get_text()

        if not ssid:
            self._show_edit_error("Enter a network name.")
            return
        if not 8 <= len(password) <= 63:
            self._show_edit_error("The password must contain 8–63 characters.")
            return

        self.operation_running = True
        self.edit_header.set_left_sensitive(False)
        self.ssid_entry.set_sensitive(False)
        self.password_entry.set_sensitive(False)
        self.show_edit_password.set_sensitive(False)
        self.save_button.set_sensitive(False)
        self.edit_error.set_visible(False)
        self.edit_busy.show_busy("Saving hotspot…")

        self.worker.submit(
            lambda: self.service.update(ssid, password),
            self._hotspot_saved,
            self._hotspot_save_failed,
        )

    def _hotspot_saved(self, info: HotspotInfo) -> None:
        self.operation_running = False
        self._restore_edit_controls()
        self.info = info
        self.password_visible = False
        self._render_info()
        self.show_page("main")
        self.service.notify(
            "Hotspot updated",
            f"{info.ssid} is using the new settings.",
        )

    def _hotspot_save_failed(self, error: Exception) -> None:
        self.operation_running = False
        self._restore_edit_controls()
        self._show_edit_error(str(error))

    def _restore_edit_controls(self) -> None:
        self.edit_header.set_left_sensitive(True)
        self.ssid_entry.set_sensitive(True)
        self.password_entry.set_sensitive(True)
        self.show_edit_password.set_sensitive(True)
        self.save_button.set_sensitive(True)
        self.edit_busy.hide_busy()

    def _show_edit_error(self, message: str) -> None:
        self.edit_error.set_label(message)
        self.edit_error.set_visible(True)

    def _back_to_main(self, _button: Gtk.Button) -> None:
        if self.operation_running:
            return
        self.show_page("main")

    def _open_settings(self, _button: Gtk.Button) -> None:
        try:
            self.service.open_settings()
        except HotspotError as error:
            self._show_main_error(str(error))

    def _show_main_error(self, message: str) -> None:
        self.clients_empty.set_label(message or "A hotspot error occurred.")

    def _background_error(self, error: Exception) -> None:
        self._show_main_error(str(error))

    def _periodic_refresh(self) -> bool:
        if self.get_visible() and not self.operation_running:
            self._refresh()
        return GLib.SOURCE_CONTINUE

    def _on_close_request(self, _window) -> bool:
        if self.refresh_source_id is not None:
            GLib.source_remove(self.refresh_source_id)
            self.refresh_source_id = None
        self.worker.shutdown()
        return False


class HotspotApplication(Adw.Application):
    def __init__(self) -> None:
        super().__init__(application_id=APP_ID)
        self.window: HotspotWindow | None = None

    def do_activate(self) -> None:
        if self.window is None:
            self.window = HotspotWindow(self)
        self.window.present()


def main() -> int:
    return HotspotApplication().run(sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
