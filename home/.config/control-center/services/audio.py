from __future__ import annotations

from dataclasses import dataclass
import os
import re
import subprocess
from typing import Iterable, Literal


class AudioError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class AudioNode:
    object_id: int
    name: str
    is_default: bool


@dataclass(frozen=True, slots=True)
class VolumeState:
    volume: int
    muted: bool


@dataclass(frozen=True, slots=True)
class AudioState:
    output: VolumeState
    microphone: VolumeState
    sinks: tuple[AudioNode, ...]
    sources: tuple[AudioNode, ...]


class AudioService:
    OUTPUT_ID = "@DEFAULT_AUDIO_SINK@"
    INPUT_ID = "@DEFAULT_AUDIO_SOURCE@"

    def _run(
        self,
        arguments: Iterable[str],
        *,
        timeout: int = 12,
        check: bool = True,
    ) -> str:
        try:
            completed = subprocess.run(
                ["wpctl", *arguments],
                text=True,
                capture_output=True,
                timeout=timeout,
                check=False,
                env={**os.environ, "LC_ALL": "C"},
            )
        except FileNotFoundError as error:
            raise AudioError("wpctl is not installed.") from error
        except subprocess.TimeoutExpired as error:
            raise AudioError("PipeWire did not answer in time.") from error

        if check and completed.returncode != 0:
            message = completed.stderr.strip() or completed.stdout.strip()
            raise AudioError(message or "The audio command failed.")

        return completed.stdout.strip()

    def get_volume(self, target: str) -> VolumeState:
        output = self._run(["get-volume", target], timeout=8)
        match = re.search(r"Volume:\s*([0-9.]+)", output)
        if match is None:
            raise AudioError("Could not read the current volume.")
        value = max(0, min(150, round(float(match.group(1)) * 100)))
        return VolumeState(volume=value, muted="[MUTED]" in output)

    def _description(self, object_id: int, fallback: str) -> str:
        output = self._run(["inspect", str(object_id)], timeout=8, check=False)
        for key in ("node.description", "node.nick", "device.description"):
            match = re.search(
                rf'^\s*\*?\s*{re.escape(key)}\s*=\s*"(.+?)"\s*$',
                output,
                re.MULTILINE,
            )
            if match:
                return match.group(1)
        return fallback

    def list_nodes(self, kind: Literal["sinks", "sources"]) -> tuple[AudioNode, ...]:
        output = self._run(["list", "audio", kind], timeout=10)
        nodes: list[AudioNode] = []

        for line in output.splitlines():
            fields = line.split("\t")
            if len(fields) < 2:
                continue
            try:
                object_id = int(fields[0].strip())
            except ValueError:
                continue
            raw_name = fields[1].strip()
            is_default = any(field.strip() == "*" for field in fields[2:])
            nodes.append(
                AudioNode(
                    object_id=object_id,
                    name=self._description(object_id, raw_name),
                    is_default=is_default,
                )
            )

        return tuple(
            sorted(nodes, key=lambda node: (not node.is_default, node.name.lower()))
        )

    def get_state(self) -> AudioState:
        return AudioState(
            output=self.get_volume(self.OUTPUT_ID),
            microphone=self.get_volume(self.INPUT_ID),
            sinks=self.list_nodes("sinks"),
            sources=self.list_nodes("sources"),
        )

    def set_volume(self, target: str, value: int) -> None:
        value = max(0, min(150, int(value)))
        self._run(
            ["set-volume", target, f"{value}%", "--limit", "1.5"],
            timeout=10,
        )

    def set_muted(self, target: str, muted: bool) -> None:
        self._run(["set-mute", target, "1" if muted else "0"], timeout=10)

    def set_default(self, node: AudioNode) -> None:
        self._run(["set-default", str(node.object_id)], timeout=10)

    def open_settings(self) -> None:
        try:
            subprocess.Popen(
                ["gnome-control-center", "sound"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
                env={**os.environ, "XDG_CURRENT_DESKTOP": "GNOME"},
            )
        except FileNotFoundError as error:
            raise AudioError("gnome-control-center is not installed.") from error

    def notify(self, title: str, message: str) -> None:
        try:
            subprocess.Popen(
                [
                    "notify-send",
                    "--app-name=Control Center",
                    "--icon=audio-card",
                    title,
                    message,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        except FileNotFoundError:
            pass
