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
from services.audio import (  # noqa: E402
    AudioError,
    AudioNode,
    AudioService,
    AudioState,
)


APP_ID = "io.github.moss.ControlCenter.Sound"
BASE_DIR = Path(__file__).resolve().parent
CSS_FILE = BASE_DIR / "common" / "style.css"


class AudioDeviceRow(Gtk.ListBoxRow):
    def __init__(self, node: AudioNode, icon: str) -> None:
        super().__init__()
        self.node = node
        self.add_css_class("network-row")

        content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        content.set_margin_top(12)
        content.set_margin_bottom(12)
        content.set_margin_start(13)
        content.set_margin_end(13)

        device_icon = Gtk.Label(label=icon)
        device_icon.add_css_class("nerd-icon")
        device_icon.add_css_class("network-icon")
        content.append(device_icon)

        name = Gtk.Label(label=node.name, xalign=0)
        name.set_ellipsize(Pango.EllipsizeMode.END)
        name.add_css_class("network-name")
        name.set_hexpand(True)
        content.append(name)

        if node.is_default:
            current = Gtk.Label(label="Current")
            current.add_css_class("connected-state")
            content.append(current)

        marker = Gtk.Label(label="")
        marker.add_css_class("nerd-icon")
        marker.add_css_class("network-arrow")
        content.append(marker)

        self.set_child(content)


class SoundWindow(BaseControlWindow):
    def __init__(self, application: Adw.Application) -> None:
        super().__init__(application, width=400, height=560)
        self.set_title("Sound")
        self.load_css(CSS_FILE)

        self.service = AudioService()
        self.worker = AsyncWorker(max_workers=4)
        self.state: AudioState | None = None
        self.operation_running = False
        self.updating_controls = False
        self.device_kind = "output"
        self.output_volume_source: int | None = None
        self.input_volume_source: int | None = None
        self.refresh_source_id: int | None = None

        self.main_header = ControlHeader(
            title="Sound",
            icon="󰕾",
            left_icon="",
            on_left_clicked=self._toggle_output_mute,
            on_close_clicked=lambda _button: self.close(),
        )
        self.main_header.set_left_tooltip("Mute output")

        self.root.append(self.stack)
        self._build_main_page()
        self._build_devices_page()
        self.show_page("main")

        self.connect("close-request", self._on_close_request)
        self._refresh()
        self.refresh_source_id = GLib.timeout_add_seconds(2, self._periodic_refresh)

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

        content.append(SectionLabel("Output"))
        output_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        output_card.add_css_class("sound-card")

        output_volume_row = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=10,
        )

        self.output_mute_button = Gtk.Button(label="󰕾")
        self.output_mute_button.add_css_class("round-control")
        self.output_mute_button.add_css_class("nerd-icon")
        self.output_mute_button.set_tooltip_text("Mute output")
        self.output_mute_button.connect(
            "clicked",
            lambda _button: self._set_channel_muted("output"),
        )
        output_volume_row.append(self.output_mute_button)

        self.output_scale = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL,
            0,
            150,
            1,
        )
        self.output_scale.set_draw_value(False)
        self.output_scale.set_hexpand(True)
        self.output_scale.connect(
            "value-changed",
            lambda scale: self._schedule_volume("output", scale.get_value()),
        )
        output_volume_row.append(self.output_scale)

        self.output_percent = Gtk.Label(label="0%")
        self.output_percent.add_css_class("volume-percent")
        output_volume_row.append(self.output_percent)
        output_card.append(output_volume_row)

        (
            self.output_device_button,
            self.output_device_value,
        ) = self._device_button("Output device")
        self.output_device_button.connect(
            "clicked",
            lambda _button: self._open_devices("output"),
        )
        output_card.append(self.output_device_button)
        content.append(output_card)

        content.append(SectionLabel("Microphone"))
        input_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        input_card.add_css_class("sound-card")

        input_volume_row = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=10,
        )

        self.input_mute_button = Gtk.Button(label="󰍭")
        self.input_mute_button.add_css_class("round-control")
        self.input_mute_button.add_css_class("nerd-icon")
        self.input_mute_button.set_tooltip_text("Mute microphone")
        self.input_mute_button.connect(
            "clicked",
            lambda _button: self._set_channel_muted("input"),
        )
        input_volume_row.append(self.input_mute_button)

        self.input_scale = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL,
            0,
            150,
            1,
        )
        self.input_scale.set_draw_value(False)
        self.input_scale.set_hexpand(True)
        self.input_scale.connect(
            "value-changed",
            lambda scale: self._schedule_volume("input", scale.get_value()),
        )
        input_volume_row.append(self.input_scale)

        self.input_percent = Gtk.Label(label="0%")
        self.input_percent.add_css_class("volume-percent")
        input_volume_row.append(self.input_percent)
        input_card.append(input_volume_row)

        (
            self.input_device_button,
            self.input_device_value,
        ) = self._device_button("Microphone device")
        self.input_device_button.connect(
            "clicked",
            lambda _button: self._open_devices("input"),
        )
        input_card.append(self.input_device_button)
        content.append(input_card)

        spacer = Gtk.Box()
        spacer.set_vexpand(True)
        content.append(spacer)

        self.settings_button = BottomActionButton("Open Sound Settings")
        self.settings_button.connect("clicked", self._open_settings)
        content.append(self.settings_button)

        self.main_busy = BusyOverlay()
        content.append(self.main_busy)

        self.stack.add_named(page, "main")

    def _device_button(
        self,
        label_text: str,
    ) -> tuple[Gtk.Button, Gtk.Label]:
        button = Gtk.Button()
        button.add_css_class("flat-info-row")

        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        text = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        text.set_hexpand(True)

        label = Gtk.Label(label=label_text, xalign=0)
        label.add_css_class("connected-strength")
        text.append(label)

        value = Gtk.Label(label="Loading…", xalign=0)
        value.add_css_class("network-name")
        value.set_ellipsize(Pango.EllipsizeMode.END)
        text.append(value)

        row.append(text)

        arrow = Gtk.Label(label="")
        arrow.add_css_class("nerd-icon")
        arrow.add_css_class("network-arrow")
        row.append(arrow)

        button.set_child(row)
        return button, value

    def _build_devices_page(self) -> None:
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.devices_header = ControlHeader(
            title="Audio Devices",
            icon="󰕾",
            left_icon="",
            on_left_clicked=self._back_to_main,
            on_close_clicked=lambda _button: self.close(),
        )
        self.devices_header.set_left_tooltip("Back")
        page.append(self.devices_header)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        content.set_margin_top(15)
        content.set_margin_bottom(15)
        content.set_margin_start(15)
        content.set_margin_end(15)
        content.set_vexpand(True)

        self.devices_section_label = SectionLabel("Available devices")
        content.append(self.devices_section_label)

        frame = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        frame.add_css_class("network-list-frame")
        frame.set_vexpand(True)

        self.devices_list = Gtk.ListBox()
        self.devices_list.set_selection_mode(Gtk.SelectionMode.NONE)
        self.devices_list.set_activate_on_single_click(True)
        self.devices_list.connect("row-activated", self._device_selected)

        self.devices_empty = Gtk.Label(label="No audio devices found.")
        self.devices_empty.set_wrap(True)
        self.devices_empty.set_margin_top(28)
        self.devices_empty.set_margin_bottom(28)
        self.devices_empty.add_css_class("empty-state")
        self.devices_list.set_placeholder(self.devices_empty)

        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroller.set_vexpand(True)
        scroller.set_child(self.devices_list)
        frame.append(scroller)
        content.append(frame)

        self.devices_busy = BusyOverlay()
        content.append(self.devices_busy)

        page.append(content)
        self.stack.add_named(page, "devices")

    def _refresh(self) -> None:
        if self.operation_running:
            return
        self.worker.submit(
            self.service.get_state,
            self._state_loaded,
            self._background_error,
        )

    def _state_loaded(self, state: AudioState) -> None:
        self.state = state
        self._render_state()

    def _render_state(self) -> None:
        if self.state is None:
            return

        self.updating_controls = True
        try:
            output = self.state.output
            microphone = self.state.microphone

            self.main_header.set_left_icon("" if output.muted else "")
            self.main_header.set_left_tooltip(
                "Unmute output" if output.muted else "Mute output"
            )

            self.output_scale.set_value(output.volume)
            self.output_percent.set_label(f"{output.volume}%")
            self.output_mute_button.set_label("󰝟" if output.muted else "󰕾")
            self.output_mute_button.set_tooltip_text(
                "Unmute output" if output.muted else "Mute output"
            )

            self.input_scale.set_value(microphone.volume)
            self.input_percent.set_label(f"{microphone.volume}%")
            self.input_mute_button.set_label(
                "󰍭" if microphone.muted else "󰍬"
            )
            self.input_mute_button.set_tooltip_text(
                "Unmute microphone" if microphone.muted else "Mute microphone"
            )

            output_name = next(
                (node.name for node in self.state.sinks if node.is_default),
                self.state.sinks[0].name if self.state.sinks else "No output device",
            )
            input_name = next(
                (node.name for node in self.state.sources if node.is_default),
                (
                    self.state.sources[0].name
                    if self.state.sources
                    else "No microphone device"
                ),
            )

            self.output_device_value.set_label(output_name)
            self.input_device_value.set_label(input_name)
        finally:
            self.updating_controls = False

    def _toggle_output_mute(self, _button: Gtk.Button) -> None:
        self._set_channel_muted("output")

    def _set_channel_muted(self, kind: str) -> None:
        if self.operation_running or self.state is None:
            return

        if kind == "output":
            current = self.state.output.muted
            target_id = self.service.OUTPUT_ID
            message = "Updating output…"
        else:
            current = self.state.microphone.muted
            target_id = self.service.INPUT_ID
            message = "Updating microphone…"

        self.operation_running = True
        self.main_header.set_left_sensitive(False)
        self.main_busy.show_busy(message)

        self.worker.submit(
            lambda: self.service.set_muted(target_id, not current),
            lambda _result: self._audio_operation_finished(),
            self._audio_operation_failed,
        )

    def _schedule_volume(self, kind: str, raw_value: float) -> None:
        if self.updating_controls:
            return

        value = int(round(raw_value))
        if kind == "output":
            self.output_percent.set_label(f"{value}%")
            if self.output_volume_source is not None:
                GLib.source_remove(self.output_volume_source)
            self.output_volume_source = GLib.timeout_add(
                140,
                self._apply_volume,
                "output",
                value,
            )
        else:
            self.input_percent.set_label(f"{value}%")
            if self.input_volume_source is not None:
                GLib.source_remove(self.input_volume_source)
            self.input_volume_source = GLib.timeout_add(
                140,
                self._apply_volume,
                "input",
                value,
            )

    def _apply_volume(self, kind: str, value: int) -> bool:
        if kind == "output":
            self.output_volume_source = None
            target = self.service.OUTPUT_ID
        else:
            self.input_volume_source = None
            target = self.service.INPUT_ID

        self.worker.submit(
            lambda: self.service.set_volume(target, value),
            lambda _result: None,
            self._background_error,
        )
        return GLib.SOURCE_REMOVE

    def _audio_operation_finished(self) -> None:
        self.operation_running = False
        self.main_header.set_left_sensitive(True)
        self.main_busy.hide_busy()
        self._refresh()

    def _audio_operation_failed(self, error: Exception) -> None:
        self.operation_running = False
        self.main_header.set_left_sensitive(True)
        self.main_busy.hide_busy()
        self._show_main_error(str(error))

    def _open_devices(self, kind: str) -> None:
        if self.state is None or self.operation_running:
            return

        self.device_kind = kind
        nodes = self.state.sinks if kind == "output" else self.state.sources
        icon = "󰕾" if kind == "output" else "󰍬"

        self.devices_section_label.set_label(
            "Output devices" if kind == "output" else "Microphone devices"
        )

        while child := self.devices_list.get_first_child():
            self.devices_list.remove(child)

        for node in nodes:
            self.devices_list.append(AudioDeviceRow(node, icon))

        self.show_page("devices")

    def _device_selected(
        self,
        _listbox: Gtk.ListBox,
        row: Gtk.ListBoxRow,
    ) -> None:
        if self.operation_running or not isinstance(row, AudioDeviceRow):
            return
        if row.node.is_default:
            self.show_page("main")
            return

        self.operation_running = True
        self.devices_header.set_left_sensitive(False)
        self.devices_list.set_sensitive(False)
        self.devices_busy.show_busy(f"Switching to {row.node.name}…")

        self.worker.submit(
            lambda: self.service.set_default(row.node),
            lambda _result: self._device_switch_succeeded(row.node),
            self._device_switch_failed,
        )

    def _device_switch_succeeded(self, node: AudioNode) -> None:
        self.operation_running = False
        self.devices_header.set_left_sensitive(True)
        self.devices_list.set_sensitive(True)
        self.devices_busy.hide_busy()
        self.service.notify("Audio device changed", node.name)
        self.show_page("main")
        self._refresh()

    def _device_switch_failed(self, error: Exception) -> None:
        self.operation_running = False
        self.devices_header.set_left_sensitive(True)
        self.devices_list.set_sensitive(True)
        self.devices_busy.hide_busy()
        self.devices_empty.set_label(str(error))

    def _back_to_main(self, _button: Gtk.Button) -> None:
        if not self.operation_running:
            self.show_page("main")

    def _open_settings(self, _button: Gtk.Button) -> None:
        try:
            self.service.open_settings()
        except AudioError as error:
            self._show_main_error(str(error))

    def _show_main_error(self, message: str) -> None:
        self.output_device_value.set_label(message or "Audio error")

    def _background_error(self, error: Exception) -> None:
        self._show_main_error(str(error))

    def _periodic_refresh(self) -> bool:
        if (
            self.get_visible()
            and not self.operation_running
            and self.stack.get_visible_child_name() == "main"
        ):
            self._refresh()
        return GLib.SOURCE_CONTINUE

    def _on_close_request(self, _window) -> bool:
        for source_id in (
            self.refresh_source_id,
            self.output_volume_source,
            self.input_volume_source,
        ):
            if source_id is not None:
                GLib.source_remove(source_id)

        self.refresh_source_id = None
        self.output_volume_source = None
        self.input_volume_source = None
        self.worker.shutdown()
        return False


class SoundApplication(Adw.Application):
    def __init__(self) -> None:
        super().__init__(application_id=APP_ID)
        self.window: SoundWindow | None = None

    def do_activate(self) -> None:
        if self.window is None:
            self.window = SoundWindow(self)
        self.window.present()


def main() -> int:
    return SoundApplication().run(sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
