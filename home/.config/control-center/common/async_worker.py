from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable

from gi.repository import GLib


class AsyncWorker:
    """Run blocking work outside GTK's main thread."""

    def __init__(self, max_workers: int = 3) -> None:
        self._executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="control-center",
        )

    def submit(
        self,
        task: Callable[[], Any],
        on_success: Callable[[Any], None],
        on_error: Callable[[Exception], None],
    ) -> None:
        future = self._executor.submit(task)

        def finished(done_future) -> None:
            try:
                result = done_future.result()
            except Exception as error:  # noqa: BLE001 - forwarded to the GTK thread
                GLib.idle_add(on_error, error)
            else:
                GLib.idle_add(on_success, result)

        future.add_done_callback(finished)

    def shutdown(self) -> None:
        self._executor.shutdown(wait=False, cancel_futures=True)
