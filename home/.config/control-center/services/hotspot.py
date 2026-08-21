from __future__ import annotations

from dataclasses import dataclass
import os
import re
import secrets
import string
import subprocess
from typing import Iterable

from services.network import _split_escaped


class HotspotError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class HotspotClient:
    ip: str
    mac: str


@dataclass(frozen=True, slots=True)
class HotspotInfo:
    enabled: bool
    profile_name: str
    ssid: str
    password: str
    interface: str
    clients: tuple[HotspotClient, ...]


class HotspotService:
    PROFILE_NAME = "Moss Hotspot"
    DEFAULT_SSID = "Moss Hotspot"

    def _run(
        self,
        arguments: Iterable[str],
        *,
        timeout: int = 30,
        show_secrets: bool = False,
        check: bool = True,
    ) -> str:
        command = ["nmcli", "--colors", "no"]
        if show_secrets:
            command.append("--show-secrets")
        command.extend(arguments)

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
            raise HotspotError("nmcli is not installed.") from error
        except subprocess.TimeoutExpired as error:
            raise HotspotError("NetworkManager did not answer in time.") from error

        if check and completed.returncode != 0:
            message = completed.stderr.strip() or completed.stdout.strip()
            raise HotspotError(message or "The hotspot command failed.")

        return completed.stdout.strip()

    def _connection_rows(self, active_only: bool) -> list[tuple[str, str, str]]:
        arguments = [
            "--terse",
            "--escape",
            "yes",
            "--fields",
            "NAME,TYPE,DEVICE",
            "connection",
            "show",
        ]
        if active_only:
            arguments.append("--active")

        output = self._run(arguments, timeout=12, check=False)
        rows: list[tuple[str, str, str]] = []
        for line in output.splitlines():
            fields = _split_escaped(line)
            if len(fields) >= 3:
                rows.append((fields[0], fields[1], fields[2]))
        return rows

    def _mode(self, profile_name: str) -> str:
        return self._run(
            [
                "--get-values",
                "802-11-wireless.mode",
                "connection",
                "show",
                profile_name,
            ],
            timeout=10,
            check=False,
        ).strip()

    def _active_hotspot(self) -> tuple[str, str] | None:
        for name, connection_type, interface in self._connection_rows(True):
            if connection_type == "802-11-wireless" and self._mode(name) == "ap":
                return name, interface
        return None

    def _saved_hotspot(self) -> str | None:
        for name, connection_type, _interface in self._connection_rows(False):
            if connection_type == "802-11-wireless" and self._mode(name) == "ap":
                return name
        return None

    def _profile_value(
        self,
        profile_name: str,
        property_name: str,
        *,
        show_secrets: bool = False,
    ) -> str:
        return self._run(
            [
                "--get-values",
                property_name,
                "connection",
                "show",
                profile_name,
            ],
            timeout=10,
            show_secrets=show_secrets,
            check=False,
        ).strip()

    @staticmethod
    def _new_password() -> str:
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(12))

    def _clients(self, interface: str) -> tuple[HotspotClient, ...]:
        if not interface:
            return ()

        try:
            completed = subprocess.run(
                ["ip", "neigh", "show", "dev", interface],
                text=True,
                capture_output=True,
                timeout=8,
                check=False,
                env={**os.environ, "LC_ALL": "C"},
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return ()

        clients: list[HotspotClient] = []
        for line in completed.stdout.splitlines():
            fields = line.split()
            if len(fields) < 4 or "lladdr" not in fields:
                continue
            state = fields[-1].upper()
            if state in {"FAILED", "INCOMPLETE", "NOARP"}:
                continue
            mac_index = fields.index("lladdr") + 1
            if mac_index >= len(fields):
                continue
            clients.append(HotspotClient(ip=fields[0], mac=fields[mac_index]))

        return tuple(clients)

    def get_info(self) -> HotspotInfo:
        active = self._active_hotspot()
        profile_name = active[0] if active else self._saved_hotspot()
        interface = active[1] if active else ""

        if profile_name is None:
            return HotspotInfo(
                enabled=False,
                profile_name=self.PROFILE_NAME,
                ssid=self.DEFAULT_SSID,
                password="",
                interface="",
                clients=(),
            )

        ssid = self._profile_value(profile_name, "802-11-wireless.ssid")
        password = self._profile_value(
            profile_name,
            "802-11-wireless-security.psk",
            show_secrets=True,
        )

        return HotspotInfo(
            enabled=active is not None,
            profile_name=profile_name,
            ssid=ssid or self.DEFAULT_SSID,
            password=password,
            interface=interface,
            clients=self._clients(interface) if active else (),
        )

    def wifi_client_connected(self) -> bool:
        for name, connection_type, _interface in self._connection_rows(True):
            if connection_type == "802-11-wireless" and self._mode(name) != "ap":
                return True
        return False

    def enable(self) -> HotspotInfo:
        self._run(["radio", "wifi", "on"], timeout=12)

        profile_name = self._saved_hotspot()
        if profile_name:
            self._run(
                ["--wait", "30", "connection", "up", profile_name],
                timeout=35,
            )
        else:
            password = self._new_password()
            self._run(
                [
                    "--wait",
                    "30",
                    "device",
                    "wifi",
                    "hotspot",
                    "con-name",
                    self.PROFILE_NAME,
                    "ssid",
                    self.DEFAULT_SSID,
                    "password",
                    password,
                ],
                timeout=35,
            )

        return self.get_info()

    def disable(self) -> HotspotInfo:
        active = self._active_hotspot()
        if active:
            self._run(
                ["--wait", "20", "connection", "down", active[0]],
                timeout=25,
            )
        return self.get_info()

    def update(self, ssid: str, password: str) -> HotspotInfo:
        info = self.get_info()
        profile_name = info.profile_name or self.PROFILE_NAME
        if self._saved_hotspot() is None:
            raise HotspotError("Enable the hotspot once before editing it.")

        self._run(
            [
                "connection",
                "modify",
                profile_name,
                "802-11-wireless.ssid",
                ssid,
                "802-11-wireless-security.key-mgmt",
                "wpa-psk",
                "802-11-wireless-security.psk",
                password,
            ],
            timeout=20,
        )

        if info.enabled:
            self._run(
                ["--wait", "20", "connection", "down", profile_name],
                timeout=25,
            )
            self._run(
                ["--wait", "30", "connection", "up", profile_name],
                timeout=35,
            )

        return self.get_info()

    def open_settings(self) -> None:
        try:
            subprocess.Popen(
                ["gnome-control-center", "network"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
                env={**os.environ, "XDG_CURRENT_DESKTOP": "GNOME"},
            )
        except FileNotFoundError as error:
            raise HotspotError("gnome-control-center is not installed.") from error

    def notify(self, title: str, message: str) -> None:
        try:
            subprocess.Popen(
                [
                    "notify-send",
                    "--app-name=Control Center",
                    "--icon=network-wireless-hotspot",
                    title,
                    message,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        except FileNotFoundError:
            pass
