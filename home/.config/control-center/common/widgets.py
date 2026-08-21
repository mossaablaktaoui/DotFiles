from __future__ import annotations

from collections.abc import Callable

from gi.repository import Gtk


class ControlHeader(Gtk.WindowHandle):
    """Reusable custom header used by every control-center window."""

    def __init__(
        self,
        title: str,
        icon: str,
        left_icon: str,
        on_left_clicked: Callable[[Gtk.Button], None],
        on_close_clicked: Callable[[Gtk.Button], None],
    ) -> None:
        super().__init__()

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        header.add_css_class("control-header")

        self.left_button = Gtk.Button(label=left_icon)
        self.left_button.add_css_class("header-button")
        self.left_button.add_css_class("nerd-icon")
        self.left_button.set_tooltip_text("Toggle")
        self.left_button.connect("clicked", on_left_clicked)
        header.append(self.left_button)

        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        title_box.set_hexpand(True)
        title_box.set_halign(Gtk.Align.CENTER)
        title_box.set_valign(Gtk.Align.CENTER)

        title_icon = Gtk.Label(label=icon)
        title_icon.add_css_class("title-icon")
        title_icon.add_css_class("nerd-icon")
        title_box.append(title_icon)

        title_label = Gtk.Label(label=title)
        title_label.add_css_class("header-title")
        title_box.append(title_label)
        header.append(title_box)

        close_button = Gtk.Button(label="")
        close_button.add_css_class("header-button")
        close_button.add_css_class("nerd-icon")
        close_button.set_tooltip_text("Close")
        close_button.connect("clicked", on_close_clicked)
        header.append(close_button)

        self.set_child(header)

    def set_left_icon(self, icon: str) -> None:
        self.left_button.set_label(icon)

    def set_left_tooltip(self, tooltip: str) -> None:
        self.left_button.set_tooltip_text(tooltip)

    def set_left_sensitive(self, sensitive: bool) -> None:
        self.left_button.set_sensitive(sensitive)


class SectionLabel(Gtk.Label):
    def __init__(self, text: str) -> None:
        super().__init__(label=text, xalign=0)
        self.add_css_class("section-label")


class BottomActionButton(Gtk.Button):
    def __init__(self, label: str, icon: str = "") -> None:
        content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        content.set_halign(Gtk.Align.CENTER)

        text = Gtk.Label(label=label)
        content.append(text)

        arrow = Gtk.Label(label=icon)
        arrow.add_css_class("nerd-icon")
        content.append(arrow)

        super().__init__()
        self.set_child(content)
        self.add_css_class("bottom-action")


class BusyOverlay(Gtk.Revealer):
    """Reusable non-blocking progress overlay."""

    def __init__(self) -> None:
        super().__init__()
        self.set_transition_type(Gtk.RevealerTransitionType.CROSSFADE)

        card = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        card.add_css_class("busy-card")
        card.set_halign(Gtk.Align.CENTER)
        card.set_valign(Gtk.Align.CENTER)

        self.spinner = Gtk.Spinner()
        card.append(self.spinner)

        self.label = Gtk.Label()
        card.append(self.label)

        self.set_child(card)

    def show_busy(self, message: str) -> None:
        self.label.set_label(message)
        self.spinner.start()
        self.set_reveal_child(True)

    def hide_busy(self) -> None:
        self.spinner.stop()
        self.set_reveal_child(False)
