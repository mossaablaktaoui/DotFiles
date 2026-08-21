from __future__ import annotations

from pathlib import Path

from gi.repository import Adw, Gdk, Gtk


class BaseControlWindow(Adw.ApplicationWindow):
    """Shared frameless window and page stack for all future controls."""

    def __init__(
        self,
        application: Adw.Application,
        *,
        width: int = 400,
        height: int = 560,
    ) -> None:
        super().__init__(application=application)
        self.set_default_size(width, height)
        self.set_resizable(False)
        self.set_decorated(False)

        self.root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.root.add_css_class("control-window")
        self.set_content(self.root)

        self.stack = Gtk.Stack()
        self.stack.set_hexpand(True)
        self.stack.set_vexpand(True)
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(220)

    def load_css(self, css_file: Path) -> None:
        provider = Gtk.CssProvider()
        provider.load_from_path(str(css_file))

        display = Gdk.Display.get_default()
        if display is not None:
            Gtk.StyleContext.add_provider_for_display(
                display,
                provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
            )

    def show_page(self, name: str) -> None:
        self.stack.set_visible_child_name(name)
