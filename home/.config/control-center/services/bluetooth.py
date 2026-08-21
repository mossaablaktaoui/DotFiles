from __future__ import annotations

from dataclasses import dataclass
import os
import re
import subprocess
from typing import Iterable


class BluetoothError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class BluetoothDevice:
    address: str
    name: str
    paired: bool
    connected: bool
    icon_name: str = ""

    @property
    def icon(self) -> str:
        value = self.icon_name.lower()
        if "head" in value or "audio" in value:
            return "󰋋"
        if "mouse" in value:
            return "󰍽"
        if "keyboard" in value:
            return "󰌌"
        if "phone" in value:
            return "󰏲"
        if "computer" in value:
            return "󰍹"
        if "game" in value:
            return "󰊴"
        return ""


class BluetoothService:
    def _run(
        self,
        arguments: Iterable[str],
        *,
        timeout: int = 20,
        check: bool = True,
    ) -> str:
        command = ["bluetoothctl", *arguments]
        try:
            completed = subprocess.run(
                command,
                text=True,
                capture_output=True,
                timeout=timeout,
                check=False,
                env={**os.environ, "LC_ALL": "C"},
            )
        except FileNotFoundError as error:
            raise BluetoothError("bluetoothctl is not installed.") from error
        except subprocess.TimeoutExpired as error:
            raise BluetoothError("Bluetooth did not answer in time.") from error

        if check and completed.returncode != 0:
            message = completed.stderr.strip() or completed.stdout.strip()
            raise BluetoothError(message or "The Bluetooth command failed.")

        return completed.stdout.strip()

    def powered(self) -> bool:
        output = self._run(["show"], timeout=8)
        match = re.search(r"^\s*Powered:\s*(yes|no)\s*$", output, re.MULTILINE)
        if match is None:
            raise BluetoothError("No Bluetooth controller was found.")
        return match.group(1) == "yes"

    def set_powered(self, powered: bool) -> None:
        output = self._run(["power", "on" if powered else "off"], timeout=12)
        if "Failed" in output:
            raise BluetoothError(output)

    @staticmethod
    def _parse_devices(output: str) -> dict[str, str]:
        devices: dict[str, str] = {}
        for line in output.splitlines():
            match = re.match(
                r"^\s*Device\s+([0-9A-Fa-f:]{17})\s+(.+?)\s*$",
                line,
            )
            if match:
                devices[match.group(1).upper()] = match.group(2)
        return devices

    def _device_info(self, address: str) -> tuple[str | None, str]:
        output = self._run(["info", address], timeout=8, check=False)
        alias_match = re.search(r"^\s*Alias:\s*(.+?)\s*$", output, re.MULTILINE)
        icon_match = re.search(r"^\s*Icon:\s*(.+?)\s*$", output, re.MULTILINE)
        alias = alias_match.group(1) if alias_match else None
        icon_name = icon_match.group(1) if icon_match else ""
        return alias, icon_name

    def scan_devices(self) -> list[BluetoothDevice]:
        # A short active scan updates BlueZ's known-device cache. The timeout
        # keeps this blocking command bounded while it runs in a worker thread.
        self._run(["--timeout", "4", "scan", "on"], timeout=7, check=False)

        all_devices = self._parse_devices(
            self._run(["devices"], timeout=10, check=False)
        )
        paired = set(
            self._parse_devices(
                self._run(["devices", "Paired"], timeout=10, check=False)
            )
        )
        connected = set(
            self._parse_devices(
                self._run(["devices", "Connected"], timeout=10, check=False)
            )
        )

        result: list[BluetoothDevice] = []
        for address, fallback_name in all_devices.items():
            alias, icon_name = self._device_info(address)
            result.append(
                BluetoothDevice(
                    address=address,
                    name=alias or fallback_name or address,
                    paired=address in paired,
                    connected=address in connected,
                    icon_name=icon_name,
                )
            )

        return sorted(
            result,
            key=lambda device: (
                not device.connected,
                not device.paired,
                device.name.lower(),
            ),
        )

    def connect(self, device: BluetoothDevice) -> None:
        output = self._run(
            ["--timeout", "25", "connect", device.address],
            timeout=30,
        )
        if "Failed" in output:
            raise BluetoothError(output)

    def disconnect(self, device: BluetoothDevice) -> None:
        output = self._run(
            ["--timeout", "15", "disconnect", device.address],
            timeout=20,
        )
        if "Failed" in output:
            raise BluetoothError(output)

    def pair(self, device: BluetoothDevice) -> None:
        # NoInputNoOutput handles common JustWorks devices without blocking for
        # terminal input. Devices requiring a PIN/passkey are delegated to the
        # full GNOME Bluetooth panel.
        output = self._run(
            [
                "--agent",
                "NoInputNoOutput",
                "--timeout",
                "35",
                "pair",
                device.address,
            ],
            timeout=40,
        )
        if "Failed" in output:
            raise BluetoothError(output)

    def open_settings(self) -> None:
        try:
            subprocess.Popen(
                ["gnome-control-center", "bluetooth"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
                env={**os.environ, "XDG_CURRENT_DESKTOP": "GNOME"},
            )
        except FileNotFoundError as error:
            raise BluetoothError("gnome-control-center is not installed.") from error

    def notify(self, title: str, message: str) -> None:
        try:
            subprocess.Popen(
                [
                    "notify-send",
                    "--app-name=Control Center",
                    "--icon=bluetooth",
                    title,
                    message,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        except FileNotFoundError:
            pass
