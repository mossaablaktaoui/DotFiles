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
from services.bluetooth import (  # noqa: E402
    BluetoothDevice,
    BluetoothError,
    BluetoothService,
)


APP_ID = "io.github.moss.ControlCenter.Bluetooth"
BASE_DIR = Path(__file__).resolve().parent
CSS_FILE = BASE_DIR / "common" / "style.css"


class BluetoothRow(Gtk.ListBoxRow):
    def __init__(self, device: BluetoothDevice) -> None:
        super().__init__()
        self.device = device
        self.add_css_class("network-row")

        content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        content.set_margin_top(11)
        content.set_margin_bottom(11)
        content.set_margin_start(13)
        content.set_margin_end(13)

        icon = Gtk.Label(label=device.icon)
        icon.add_css_class("nerd-icon")
        icon.add_css_class("network-icon")
        content.append(icon)

        name_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        name_box.set_hexpand(True)

        name = Gtk.Label(label=device.name, xalign=0)
        name.set_ellipsize(Pango.EllipsizeMode.END)
        name.add_css_class("network-name")
        name_box.append(name)

        state_text = ""
        if device.connected:
            state_text = "Connected"
        elif device.paired:
            state_text = "Paired"

        if state_text:
            state = Gtk.Label(label=state_text, xalign=0)
            state.add_css_class(
                "connected-state" if device.connected else "device-state"
            )
            name_box.append(state)

        content.append(name_box)

        action = Gtk.Label(
            label=(
                "Disconnect"
                if device.connected
                else "Connect"
                if device.paired
                else "Pair"
            )
        )
        action.add_css_class("row-action")
        content.append(action)

        arrow = Gtk.Label(label="")
        arrow.add_css_class("nerd-icon")
        arrow.add_css_class("network-arrow")
        content.append(arrow)

        self.set_child(content)


class BluetoothWindow(BaseControlWindow):
    def __init__(self, application: Adw.Application) -> None:
        super().__init__(application, width=400, height=600)
        self.set_title("Bluetooth")
        self.load_css(CSS_FILE)

        self.service = BluetoothService()
        self.worker = AsyncWorker()
        self.devices: list[BluetoothDevice] = []
        self.selected_device: BluetoothDevice | None = None
        self.bluetooth_enabled = False
        self.operation_running = False
        self.scan_running = False
        self.refresh_source_id: int | None = None

        self.main_header = ControlHeader(
            title="Bluetooth",
            icon="",
            left_icon="",
            on_left_clicked=self._toggle_power,
            on_close_clicked=lambda _button: self.close(),
        )
        self.main_header.set_left_tooltip("Turn Bluetooth on")

        self.root.append(self.stack)
        self._build_main_page()
        self._build_pair_page()
        self.show_page("main")

        self.connect("close-request", self._on_close_request)
        self._refresh()
        self.refresh_source_id = GLib.timeout_add_seconds(7, self._periodic_refresh)

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

        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroller.set_vexpand(True)

        sections = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        scroller.set_child(sections)

        self.connected_section, self.connected_list = self._make_section(
            "Connected", "No connected devices."
        )
        sections.append(self.connected_section)

        self.paired_section, self.paired_list = self._make_section(
            "Paired", "No paired devices."
        )
        sections.append(self.paired_section)

        self.available_section, self.available_list = self._make_section(
            "Available", "Searching for devices…"
        )
        sections.append(self.available_section)

        for listbox in (
            self.connected_list,
            self.paired_list,
            self.available_list,
        ):
            listbox.connect("row-activated", self._device_activated)

        self.main_body.append(scroller)

        self.settings_button = BottomActionButton("Open Bluetooth Settings")
        self.settings_button.connect("clicked", self._open_settings)
        self.main_body.append(self.settings_button)

        self.main_busy = BusyOverlay()
        content.append(self.main_busy)

        self.stack.add_named(page, "main")

    def _make_section(
        self,
        title: str,
        empty_text: str,
    ) -> tuple[Gtk.Box, Gtk.ListBox]:
        section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        section.append(SectionLabel(title))

        frame = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        frame.add_css_class("network-list-frame")

        listbox = Gtk.ListBox()
        listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        listbox.set_activate_on_single_click(True)

        empty = Gtk.Label(label=empty_text)
        empty.set_wrap(True)
        empty.set_margin_top(20)
        empty.set_margin_bottom(20)
        empty.add_css_class("empty-state")
        listbox.set_placeholder(empty)

        frame.append(listbox)
        section.append(frame)
        return section, listbox

    def _build_pair_page(self) -> None:
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.pair_header = ControlHeader(
            title="Pair Device",
            icon="",
            left_icon="",
            on_left_clicked=self._back_to_main,
            on_close_clicked=lambda _button: self.close(),
        )
        self.pair_header.set_left_tooltip("Back")
        page.append(self.pair_header)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content.set_margin_top(28)
        content.set_margin_bottom(18)
        content.set_margin_start(18)
        content.set_margin_end(18)
        content.set_vexpand(True)

        self.pair_icon = Gtk.Label(label="")
        self.pair_icon.add_css_class("nerd-icon")
        self.pair_icon.add_css_class("pair-device-icon")
        content.append(self.pair_icon)

        self.pair_name = Gtk.Label(label="")
        self.pair_name.set_wrap(True)
        self.pair_name.set_justify(Gtk.Justification.CENTER)
        self.pair_name.add_css_class("password-network")
        content.append(self.pair_name)

        explanation = Gtk.Label(
            label="Pair with this device?",
        )
        explanation.add_css_class("connected-strength")
        content.append(explanation)

        self.pair_error = Gtk.Label(label="")
        self.pair_error.set_wrap(True)
        self.pair_error.set_justify(Gtk.Justification.CENTER)
        self.pair_error.add_css_class("error-label")
        self.pair_error.set_visible(False)
        content.append(self.pair_error)

        spacer = Gtk.Box()
        spacer.set_vexpand(True)
        content.append(spacer)

        actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        actions.set_homogeneous(True)

        self.cancel_pair_button = Gtk.Button(label="Cancel")
        self.cancel_pair_button.add_css_class("secondary-action")
        self.cancel_pair_button.connect("clicked", self._back_to_main)
        actions.append(self.cancel_pair_button)

        self.pair_button = Gtk.Button(label="Pair")
        self.pair_button.add_css_class("suggested-action")
        self.pair_button.add_css_class("connect-button")
        self.pair_button.connect("clicked", self._pair_selected)
        actions.append(self.pair_button)

        content.append(actions)

        self.pair_busy = BusyOverlay()
        content.append(self.pair_busy)

        page.append(content)
        self.stack.add_named(page, "pair")

    def _refresh(self) -> None:
        if self.operation_running:
            return
        self.worker.submit(
            self.service.powered,
            self._power_loaded,
            self._background_error,
        )

    def _power_loaded(self, enabled: bool) -> None:
        self._set_power_state(enabled)
        if enabled:
            self._scan()
        else:
            self._clear_devices()

    def _set_power_state(self, enabled: bool) -> None:
        self.bluetooth_enabled = enabled
        self.main_header.set_left_icon("" if enabled else "")
        self.main_header.set_left_tooltip(
            "Turn Bluetooth off" if enabled else "Turn Bluetooth on"
        )
        self.main_body.set_visible(enabled)

    def _toggle_power(self, _button: Gtk.Button) -> None:
        if self.operation_running:
            return

        target = not self.bluetooth_enabled
        self.operation_running = True
        self.main_header.set_left_sensitive(False)
        self.main_busy.show_busy(
            "Turning Bluetooth on…" if target else "Turning Bluetooth off…"
        )

        self.worker.submit(
            lambda: self.service.set_powered(target),
            lambda _result: self._power_finished(target),
            self._power_failed,
        )

    def _power_finished(self, enabled: bool) -> None:
        self.operation_running = False
        self.main_header.set_left_sensitive(True)
        self.main_busy.hide_busy()
        self._set_power_state(enabled)
        if enabled:
            self._scan()
        else:
            self._clear_devices()

    def _power_failed(self, error: Exception) -> None:
        self.operation_running = False
        self.main_header.set_left_sensitive(True)
        self.main_busy.hide_busy()
        self._set_available_placeholder(str(error))
        self._refresh()

    def _scan(self) -> None:
        if self.scan_running or self.operation_running or not self.bluetooth_enabled:
            return
        self.scan_running = True
        self.worker.submit(
            self.service.scan_devices,
            self._devices_loaded,
            self._scan_failed,
        )

    def _devices_loaded(self, devices: list[BluetoothDevice]) -> None:
        self.scan_running = False
        self.devices = devices
        self._render_devices()

    def _scan_failed(self, error: Exception) -> None:
        self.scan_running = False
        self._set_available_placeholder(str(error))

    @staticmethod
    def _clear_list(listbox: Gtk.ListBox) -> None:
        while child := listbox.get_first_child():
            listbox.remove(child)

    def _clear_lists(self) -> None:
        for listbox in (
            self.connected_list,
            self.paired_list,
            self.available_list,
        ):
            self._clear_list(listbox)

    def _clear_devices(self) -> None:
        self.devices = []
        self._clear_lists()

    def _render_devices(self) -> None:
        self._clear_lists()
        for device in self.devices:
            if device.connected:
                self.connected_list.append(BluetoothRow(device))
            elif device.paired:
                self.paired_list.append(BluetoothRow(device))
            else:
                self.available_list.append(BluetoothRow(device))

    def _set_available_placeholder(self, message: str) -> None:
        placeholder = self.available_list.get_placeholder()
        if isinstance(placeholder, Gtk.Label):
            placeholder.set_label(message)

    def _device_activated(
        self,
        _listbox: Gtk.ListBox,
        row: Gtk.ListBoxRow,
    ) -> None:
        if self.operation_running or not isinstance(row, BluetoothRow):
            return

        device = row.device
        if device.connected:
            self._start_device_operation(
                device,
                "Disconnecting",
                lambda: self.service.disconnect(device),
                "Bluetooth disconnected",
                f"Disconnected from {device.name}",
            )
        elif device.paired:
            self._start_device_operation(
                device,
                "Connecting",
                lambda: self.service.connect(device),
                "Bluetooth connected",
                f"Connected to {device.name}",
            )
        else:
            self._open_pair_page(device)

    def _open_pair_page(self, device: BluetoothDevice) -> None:
        self.selected_device = device
        self.pair_icon.set_label(device.icon)
        self.pair_name.set_label(device.name)
        self.pair_error.set_visible(False)
        self.pair_button.set_sensitive(True)
        self.cancel_pair_button.set_sensitive(True)
        self.pair_header.set_left_sensitive(True)
        self.pair_busy.hide_busy()
        self.show_page("pair")

    def _back_to_main(self, _button: Gtk.Button) -> None:
        if self.operation_running:
            return
        self.selected_device = None
        self.pair_error.set_visible(False)
        self.show_page("main")

    def _pair_selected(self, _button: Gtk.Button) -> None:
        if self.operation_running or self.selected_device is None:
            return

        device = self.selected_device
        self.operation_running = True
        self.pair_button.set_sensitive(False)
        self.cancel_pair_button.set_sensitive(False)
        self.pair_header.set_left_sensitive(False)
        self.pair_error.set_visible(False)
        self.pair_busy.show_busy(f"Pairing with {device.name}…")

        self.worker.submit(
            lambda: self.service.pair(device),
            lambda _result: self._pair_succeeded(device),
            self._pair_failed,
        )

    def _pair_succeeded(self, device: BluetoothDevice) -> None:
        self.operation_running = False
        self._restore_pair_controls()
        self.service.notify(
            "Bluetooth paired",
            f"Paired and connected to {device.name}",
        )
        self.selected_device = None
        self.show_page("main")
        self._scan()

    def _pair_failed(self, error: Exception) -> None:
        self.operation_running = False
        self._restore_pair_controls()
        message = str(error).strip()
        if any(
            word in message.lower() for word in ("authentication", "passkey", "pin")
        ):
            message = (
                "This device needs passkey confirmation. "
                "Use Open Bluetooth Settings to pair it."
            )
        self.pair_error.set_label(message or "Could not pair with this device.")
        self.pair_error.set_visible(True)

    def _restore_pair_controls(self) -> None:
        self.pair_button.set_sensitive(True)
        self.cancel_pair_button.set_sensitive(True)
        self.pair_header.set_left_sensitive(True)
        self.pair_busy.hide_busy()

    def _start_device_operation(
        self,
        device: BluetoothDevice,
        action: str,
        task,
        notification_title: str,
        notification_message: str,
    ) -> None:
        self.operation_running = True
        self.main_header.set_left_sensitive(False)
        self.main_body.set_sensitive(False)
        self.main_busy.show_busy(f"{action} {device.name}…")

        self.worker.submit(
            task,
            lambda _result: self._device_operation_succeeded(
                notification_title,
                notification_message,
            ),
            self._device_operation_failed,
        )

    def _device_operation_succeeded(
        self,
        notification_title: str,
        notification_message: str,
    ) -> None:
        self.operation_running = False
        self.main_header.set_left_sensitive(True)
        self.main_body.set_sensitive(True)
        self.main_busy.hide_busy()
        self.service.notify(notification_title, notification_message)
        self._scan()

    def _device_operation_failed(self, error: Exception) -> None:
        self.operation_running = False
        self.main_header.set_left_sensitive(True)
        self.main_body.set_sensitive(True)
        self.main_busy.hide_busy()
        self._set_available_placeholder(str(error))

    def _open_settings(self, _button: Gtk.Button) -> None:
        try:
            self.service.open_settings()
        except BluetoothError as error:
            self._set_available_placeholder(str(error))

    def _background_error(self, error: Exception) -> None:
        self._set_available_placeholder(str(error))

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


class BluetoothApplication(Adw.Application):
    def __init__(self) -> None:
        super().__init__(application_id=APP_ID)
        self.window: BluetoothWindow | None = None

    def do_activate(self) -> None:
        if self.window is None:
            self.window = BluetoothWindow(self)
        self.window.present()


def main() -> int:
    return BluetoothApplication().run(sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
