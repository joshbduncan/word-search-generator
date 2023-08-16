from time import monotonic

from textual.reactive import reactive
from textual.widgets import Static


class Timer(Static):
    """A widget to display elapsed time."""

    start_time = reactive(monotonic)  # type: ignore
    time = reactive(0.0)
    stop: bool = False

    def on_mount(self) -> None:
        self.set_interval(1 / 60, self.update_time)

    def update_time(self) -> None:
        if not self.stop:
            self.time = monotonic() - self.start_time  # type: ignore[operator]

    def stop_time(self) -> None:
        self.time = self.time

    def watch_time(self, time: float) -> None:
        minutes, seconds = divmod(time, 60)
        hours, minutes = divmod(minutes, 60)
        self.update(f"Elapsed Time: {hours:02,.0f}:{minutes:02.0f}:{seconds:05.2f}")
