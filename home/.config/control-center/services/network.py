from __future__ import annotations

from dataclasses import dataclass
import os
import subprocess
from typing import Iterable


class NetworkError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class WifiNetwork:
    ssid: str
    signal: int
    security: str
    active: bool = False

    @property
    def secured(self) -> bool:
        value = self.security.strip().lower()
        return bool(value and value not in {"--", "none", "open"})

    @property
    def signal_icon(self) -> str:
        if self.signal >= 80:
            return "󰤨"
        if self.signal >= 60:
            return "󰤥"
        if self.signal >= 40:
            return "󰤢"
        if self.signal >= 20:
            return "󰤟"
        return "󰤯"


def _split_escaped(line: str, separator: str = ":") -> list[str]:
    """Split nmcli terse output while respecting backslash escaping."""

    fields: list[str] = []
    current: list[str] = []
    escaped = False

    for character in line:
        if escaped:
            current.append(character)
            escaped = False
        elif character == "\\":
            escaped = True
        elif character == separator:
            fields.append("".join(current))
            current = []
        else:
            current.append(character)

    if escaped:
        current.append("\\")

    fields.append("".join(current))
    return fields


class NetworkService:
    """Small NetworkManager backend based on nmcli."""

    def _run(
        self,
        arguments: Iterable[str],
        *,
        input_text: str | None = None,
        timeout: int = 35,
    ) -> str:
        command = ["nmcli", "--colors", "no", *arguments]

        try:
            completed = subprocess.run(
                command,
                input=input_text,
                text=True,
                capture_output=True,
                timeout=timeout,
                check=False,
                env={**os.environ, "LC_ALL": "C"},
            )
        except FileNotFoundError as error:
            raise NetworkError("nmcli is not installed.") from error
        except subprocess.TimeoutExpired as error:
            raise NetworkError("NetworkManager did not answer in time.") from error

        if completed.returncode != 0:
            message = completed.stderr.strip() or completed.stdout.strip()
            raise NetworkError(message or "The NetworkManager command failed.")

        return completed.stdout.strip()

    def wifi_enabled(self) -> bool:
        value = self._run(["radio", "wifi"], timeout=8)
        return value.strip().lower() == "enabled"

    def set_wifi_enabled(self, enabled: bool) -> None:
        self._run(["radio", "wifi", "on" if enabled else "off"], timeout=15)

    def scan_networks(self) -> list[WifiNetwork]:
        output = self._run(
            [
                "--terse",
                "--escape",
                "yes",
                "--fields",
                "IN-USE,SSID,SIGNAL,SECURITY",
                "device",
                "wifi",
                "list",
                "--rescan",
                "auto",
            ],
            timeout=20,
        )

        strongest_by_ssid: dict[str, WifiNetwork] = {}

        for line in output.splitlines():
            fields = _split_escaped(line)
            if len(fields) < 4:
                continue

            in_use, ssid, signal_text, security = fields[:4]
            ssid = ssid.strip()

            if not ssid or ssid == "--":
                continue

            try:
                signal = max(0, min(100, int(signal_text)))
            except ValueError:
                signal = 0

            network = WifiNetwork(
                ssid=ssid,
                signal=signal,
                security=security.strip(),
                active=in_use.strip() in {"*", "yes"},
            )

            previous = strongest_by_ssid.get(ssid)
            if previous is None or network.signal > previous.signal or network.active:
                strongest_by_ssid[ssid] = network

        return sorted(
            strongest_by_ssid.values(),
            key=lambda network: (not network.active, -network.signal, network.ssid.lower()),
        )

    def connect(self, network: WifiNetwork, password: str | None = None) -> None:
        arguments = ["--wait", "30"]

        if password is None:
            arguments.extend(["device", "wifi", "connect", network.ssid])
            self._run(arguments, timeout=35)
            return

        arguments.extend(
            ["device", "wifi", "connect", network.ssid, "password", password]
        )
        self._run(arguments, timeout=35)

    def open_wifi_settings(self) -> None:
        environment = {
            **os.environ,
            "XDG_CURRENT_DESKTOP": "GNOME",
        }

        try:
            subprocess.Popen(
                ["gnome-control-center", "wifi"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
                env=environment,
            )
        except FileNotFoundError as error:
            raise NetworkError("gnome-control-center is not installed.") from error

    def send_connected_notification(self, ssid: str) -> None:
        try:
            subprocess.Popen(
                [
                    "notify-send",
                    "--app-name=Control Center",
                    "--icon=network-wireless",
                    "Wi-Fi connected",
                    f"Connected to {ssid}",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        except FileNotFoundError:
            # A successful connection must not be treated as failed only because
            # notifications are unavailable.
            pass
