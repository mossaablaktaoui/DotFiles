#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, GLib, Gtk, Pango  # noqa: E402

from common.async_worker import AsyncWorker  # noqa: E402
from common.widgets import (  # noqa: E402
    BottomActionButton,
    BusyOverlay,
    ControlHeader,
    SectionLabel,
)
from common.window import BaseControlWindow  # noqa: E402
from services.network import NetworkError, NetworkService, WifiNetwork  # noqa: E402


APP_ID = "io.github.moss.ControlCenter.Wifi"
BASE_DIR = Path(__file__).resolve().parent
CSS_FILE = BASE_DIR / "common" / "style.css"


class WifiRow(Gtk.ListBoxRow):
    def __init__(self, network: WifiNetwork) -> None:
        super().__init__()
        self.network = network
        self.add_css_class("network-row")

        content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        content.set_margin_top(11)
        content.set_margin_bottom(11)
        content.set_margin_start(13)
        content.set_margin_end(13)

        signal_icon = Gtk.Label(label=network.signal_icon)
        signal_icon.add_css_class("nerd-icon")
        signal_icon.add_css_class("network-icon")
        content.append(signal_icon)

        name_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        name_box.set_hexpand(True)

        ssid = Gtk.Label(label=network.ssid, xalign=0)
        ssid.set_ellipsize(Pango.EllipsizeMode.END)
        ssid.add_css_class("network-name")
        name_box.append(ssid)

        if network.active:
            state = Gtk.Label(label="Connected", xalign=0)
            state.add_css_class("connected-state")
            name_box.append(state)

        content.append(name_box)

        strength = Gtk.Label(label=f"{network.signal}%")
        strength.add_css_class("network-strength")
        content.append(strength)

        if network.secured:
            lock = Gtk.Label(label="")
            lock.add_css_class("nerd-icon")
            lock.add_css_class("network-lock")
            content.append(lock)

        arrow = Gtk.Label(label="")
        arrow.add_css_class("nerd-icon")
        arrow.add_css_class("network-arrow")
        content.append(arrow)

        self.set_child(content)


class WifiWindow(BaseControlWindow):
    def __init__(self, application: Adw.Application) -> None:
        super().__init__(application, width=400, height=560)
        self.set_title("Wi-Fi")
        self.load_css(CSS_FILE)

        self.service = NetworkService()
        self.worker = AsyncWorker()
        self.networks: list[WifiNetwork] = []
        self.selected_network: WifiNetwork | None = None
        self.wifi_is_enabled = False
        self.scan_running = False
        self.operation_running = False
        self.refresh_source_id: int | None = None

        self.main_header = ControlHeader(
            title="  Wi-Fi",
            icon="",
            left_icon="",
            on_left_clicked=self._toggle_wifi,
            on_close_clicked=lambda _button: self.close(),
        )
        self.main_header.set_left_tooltip("Turn Wi-Fi on")
        self.root.append(self.stack)

        self._build_main_page()
        self._build_password_page()
        self.show_page("main")

        self.connect("close-request", self._on_close_request)

        self._refresh_everything()
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

        connected_card = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        connected_card.add_css_class("connected-card")

        self.connected_icon = Gtk.Label(label="󰤯")
        self.connected_icon.add_css_class("nerd-icon")
        self.connected_icon.add_css_class("connected-icon")
        connected_card.append(self.connected_icon)

        connected_text = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        connected_text.set_hexpand(True)

        self.connected_label = Gtk.Label(label="Not connected", xalign=0)
        self.connected_label.add_css_class("connected-label")
        connected_text.append(self.connected_label)

        self.connected_strength = Gtk.Label(label="", xalign=0)
        self.connected_strength.add_css_class("connected-strength")
        connected_text.append(self.connected_strength)

        connected_card.append(connected_text)
        self.main_body.append(connected_card)

        self.main_body.append(SectionLabel("Available networks"))

        list_frame = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        list_frame.add_css_class("network-list-frame")
        list_frame.set_vexpand(True)

        self.network_list = Gtk.ListBox()
        self.network_list.set_selection_mode(Gtk.SelectionMode.NONE)
        self.network_list.set_activate_on_single_click(True)
        self.network_list.connect("row-activated", self._network_activated)

        self.empty_label = Gtk.Label(label="Searching for networks…")
        self.empty_label.set_wrap(True)
        self.empty_label.set_margin_top(28)
        self.empty_label.set_margin_bottom(28)
        self.empty_label.add_css_class("empty-state")
        self.network_list.set_placeholder(self.empty_label)

        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroller.set_propagate_natural_height(False)
        scroller.set_vexpand(True)
        scroller.set_child(self.network_list)

        list_frame.append(scroller)
        self.main_body.append(list_frame)

        self.settings_button = BottomActionButton("Open Wi-Fi Settings")
        self.settings_button.connect("clicked", self._open_settings)
        self.main_body.append(self.settings_button)

        self.main_busy = BusyOverlay()
        content.append(self.main_busy)

        self.stack.add_named(page, "main")

    def _build_password_page(self) -> None:
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.password_header = ControlHeader(
            title="Connect to Wi-Fi",
            icon="",
            left_icon="",
            on_left_clicked=self._back_to_main,
            on_close_clicked=lambda _button: self.close(),
        )
        self.password_header.set_left_tooltip("Back")
        page.append(self.password_header)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        content.set_margin_top(22)
        content.set_margin_bottom(18)
        content.set_margin_start(18)
        content.set_margin_end(18)
        content.set_vexpand(True)

        self.password_network_name = Gtk.Label(label="", xalign=0)
        self.password_network_name.add_css_class("password-network")
        self.password_network_name.set_wrap(True)
        content.append(self.password_network_name)

        content.append(SectionLabel("Password"))

        self.password_entry = Gtk.Entry()
        self.password_entry.set_visibility(False)
        self.password_entry.set_input_purpose(Gtk.InputPurpose.PASSWORD)
        self.password_entry.set_hexpand(True)
        self.password_entry.connect("activate", self._connect_from_password)
        content.append(self.password_entry)

        self.show_password = Gtk.CheckButton(label="Show password")
        self.show_password.connect("toggled", self._toggle_password_visibility)
        content.append(self.show_password)

        self.password_error = Gtk.Label(label="", xalign=0)
        self.password_error.set_wrap(True)
        self.password_error.add_css_class("error-label")
        self.password_error.set_visible(False)
        content.append(self.password_error)

        spacer = Gtk.Box()
        spacer.set_vexpand(True)
        content.append(spacer)

        self.connect_button = Gtk.Button(label="Connect")
        self.connect_button.add_css_class("suggested-action")
        self.connect_button.add_css_class("connect-button")
        self.connect_button.connect("clicked", self._connect_from_password)
        content.append(self.connect_button)

        self.password_busy = BusyOverlay()
        content.append(self.password_busy)

        page.append(content)
        self.stack.add_named(page, "password")

    def _refresh_everything(self) -> None:
        if self.operation_running:
            return

        self.worker.submit(
            self.service.wifi_enabled,
            self._wifi_state_loaded,
            self._background_error,
        )

    def _wifi_state_loaded(self, enabled: bool) -> None:
        self._set_wifi_visual_state(enabled)

        if enabled:
            self._scan_networks()
        else:
            self._clear_networks()

    def _set_wifi_visual_state(self, enabled: bool) -> None:
        self.wifi_is_enabled = enabled
        self.main_header.set_left_icon("" if enabled else "")
        self.main_header.set_left_tooltip(
            "Turn Wi-Fi off" if enabled else "Turn Wi-Fi on"
        )
        self.main_body.set_visible(enabled)

    def _toggle_wifi(self, _button: Gtk.Button) -> None:
        if self.operation_running:
            return

        target_state = not self.wifi_is_enabled
        self.operation_running = True
        self.main_header.set_left_sensitive(False)
        self.main_busy.show_busy(
            "Turning Wi-Fi on…" if target_state else "Turning Wi-Fi off…"
        )

        self.worker.submit(
            lambda: self.service.set_wifi_enabled(target_state),
            lambda _result: self._wifi_toggle_finished(target_state),
            self._wifi_toggle_failed,
        )

    def _wifi_toggle_finished(self, enabled: bool) -> None:
        self.operation_running = False
        self.main_header.set_left_sensitive(True)
        self.main_busy.hide_busy()
        self._set_wifi_visual_state(enabled)

        if enabled:
            self.empty_label.set_label("Searching for networks…")
            self._scan_networks()
        else:
            self._clear_networks()

    def _wifi_toggle_failed(self, error: Exception) -> None:
        self.operation_running = False
        self.main_header.set_left_sensitive(True)
        self.main_busy.hide_busy()
        self._show_main_error(str(error))
        self._refresh_everything()

    def _scan_networks(self) -> None:
        if self.scan_running or self.operation_running or not self.wifi_is_enabled:
            return

        self.scan_running = True
        self.worker.submit(
            self.service.scan_networks,
            self._networks_loaded,
            self._scan_failed,
        )

    def _networks_loaded(self, networks: list[WifiNetwork]) -> None:
        self.scan_running = False
        self.networks = networks
        self._render_networks(networks)

    def _scan_failed(self, error: Exception) -> None:
        self.scan_running = False
        self.empty_label.set_label(str(error) or "Could not scan Wi-Fi networks.")

    def _render_networks(self, networks: list[WifiNetwork]) -> None:
        while child := self.network_list.get_first_child():
            self.network_list.remove(child)

        connected = next((network for network in networks if network.active), None)

        if connected is None:
            self.connected_icon.set_label("󰤯")
            self.connected_label.set_label("Not connected")
            self.connected_strength.set_label("")
        else:
            self.connected_icon.set_label(connected.signal_icon)
            self.connected_label.set_label(f"Connected to {connected.ssid}")
            self.connected_strength.set_label(f"Wi-Fi strength: {connected.signal}%")

        if not networks:
            self.empty_label.set_label("No Wi-Fi networks found.")
            return

        for network in networks:
            self.network_list.append(WifiRow(network))

    def _clear_networks(self) -> None:
        self.networks = []
        while child := self.network_list.get_first_child():
            self.network_list.remove(child)

        self.connected_icon.set_label("󰤯")
        self.connected_label.set_label("Not connected")
        self.connected_strength.set_label("")

    def _network_activated(
        self,
        _listbox: Gtk.ListBox,
        row: Gtk.ListBoxRow,
    ) -> None:
        if self.operation_running or not isinstance(row, WifiRow):
            return

        network = row.network
        if network.active:
            return

        if network.secured:
            self._open_password_page(network)
        else:
            self._start_connection(network, password=None, from_password_page=False)

    def _open_password_page(self, network: WifiNetwork) -> None:
        self.selected_network = network
        self.password_network_name.set_label(f"Connect to “{network.ssid}”")
        self.password_entry.set_text("")
        self.show_password.set_active(False)
        self.password_entry.set_visibility(False)
        self.password_error.set_visible(False)
        self.password_busy.hide_busy()
        self.connect_button.set_sensitive(True)
        self.password_header.set_left_sensitive(True)
        self.show_page("password")
        GLib.idle_add(self.password_entry.grab_focus)

    def _back_to_main(self, _button: Gtk.Button) -> None:
        if self.operation_running:
            return

        self.selected_network = None
        self.password_entry.set_text("")
        self.password_error.set_visible(False)
        self.show_page("main")

    def _toggle_password_visibility(self, button: Gtk.CheckButton) -> None:
        self.password_entry.set_visibility(button.get_active())

    def _connect_from_password(self, _widget) -> None:
        if self.operation_running or self.selected_network is None:
            return

        password = self.password_entry.get_text()
        if not password:
            self._show_password_error("Enter the Wi-Fi password.")
            return

        self._start_connection(
            self.selected_network,
            password=password,
            from_password_page=True,
        )

    def _start_connection(
        self,
        network: WifiNetwork,
        *,
        password: str | None,
        from_password_page: bool,
    ) -> None:
        self.operation_running = True

        if from_password_page:
            self.password_error.set_visible(False)
            self.password_header.set_left_sensitive(False)
            self.password_entry.set_sensitive(False)
            self.show_password.set_sensitive(False)
            self.connect_button.set_sensitive(False)
            self.connect_button.set_label("Connecting…")
            self.password_busy.show_busy(f"Connecting to {network.ssid}…")
        else:
            self.main_header.set_left_sensitive(False)
            self.network_list.set_sensitive(False)
            self.settings_button.set_sensitive(False)
            self.main_busy.show_busy(f"Connecting to {network.ssid}…")

        self.worker.submit(
            lambda: self.service.connect(network, password),
            lambda _result: self._connection_succeeded(network),
            lambda error: self._connection_failed(error, from_password_page),
        )

    def _connection_succeeded(self, network: WifiNetwork) -> None:
        self.operation_running = False
        self._restore_connection_controls()
        self.service.send_connected_notification(network.ssid)

        self.selected_network = None
        self.password_entry.set_text("")
        self.show_page("main")
        self.empty_label.set_label("Refreshing networks…")
        self._scan_networks()

    def _connection_failed(
        self,
        error: Exception,
        from_password_page: bool,
    ) -> None:
        self.operation_running = False
        self._restore_connection_controls()

        message = self._friendly_connection_error(error)
        if from_password_page:
            self._show_password_error(message)
            self.password_entry.grab_focus()
        else:
            self._show_main_error(message)

    def _restore_connection_controls(self) -> None:
        self.main_header.set_left_sensitive(True)
        self.network_list.set_sensitive(True)
        self.settings_button.set_sensitive(True)
        self.main_busy.hide_busy()

        self.password_header.set_left_sensitive(True)
        self.password_entry.set_sensitive(True)
        self.show_password.set_sensitive(True)
        self.connect_button.set_sensitive(True)
        self.connect_button.set_label("Connect")
        self.password_busy.hide_busy()

    def _friendly_connection_error(self, error: Exception) -> str:
        message = str(error).strip()
        lowered = message.lower()

        if "secrets were required" in lowered or "password" in lowered:
            return "The password is incorrect or was rejected."
        if "no network with ssid" in lowered:
            return "This network is no longer available."
        if "activation failed" in lowered:
            return "Could not connect. Check the password and try again."
        return message or "Could not connect to this Wi-Fi network."

    def _show_password_error(self, message: str) -> None:
        self.password_error.set_label(message)
        self.password_error.set_visible(True)

    def _show_main_error(self, message: str) -> None:
        self.empty_label.set_label(message)

    def _open_settings(self, _button: Gtk.Button) -> None:
        try:
            self.service.open_wifi_settings()
        except NetworkError as error:
            self._show_main_error(str(error))

    def _background_error(self, error: Exception) -> None:
        self._show_main_error(str(error))

    def _periodic_refresh(self) -> bool:
        if self.get_visible() and not self.operation_running:
            self._refresh_everything()
        return GLib.SOURCE_CONTINUE

    def _on_close_request(self, _window) -> bool:
        if self.refresh_source_id is not None:
            GLib.source_remove(self.refresh_source_id)
            self.refresh_source_id = None

        self.worker.shutdown()
        return False


class WifiApplication(Adw.Application):
    def __init__(self) -> None:
        super().__init__(application_id=APP_ID)
        self.window: WifiWindow | None = None

    def do_activate(self) -> None:
        if self.window is None:
            self.window = WifiWindow(self)

        self.window.present()


def main() -> int:
    app = WifiApplication()
    return app.run(sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
