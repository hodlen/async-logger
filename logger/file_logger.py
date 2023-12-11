import asyncio
from datetime import date, datetime
from collections import deque
from io import TextIOWrapper
from pathlib import Path
import sys
from typing import Deque, Optional, Tuple
from logger.base import Clock, ILog


class FileLogger(ILog):
    _stopped = False
    _msg_queue: Deque[Tuple[str, datetime]] = deque()
    _logging_dir: Path
    _last_log_date: Optional[date] = None
    _current_log_file: Optional[TextIOWrapper] = None
    _clock: Clock = datetime.now

    def __init__(self, logging_dir: Path, logic_clock: Optional[Clock] = None):
        super().__init__()
        self._logging_dir = logging_dir
        self._logging_dir.mkdir(parents=True, exist_ok=True)
        if logic_clock is not None:
            self._clock = logic_clock
        self._task = asyncio.run_coroutine_threadsafe(
            self._loop_save(), asyncio.get_event_loop()
        )
        self._task.add_done_callback(
            lambda _: self._current_log_file.close()
            if self._current_log_file is not None
            else None
        )

    def write(self, log_message: str):
        if self._stopped:
            raise RuntimeError("Cannot write to a stopped logger.")
        self._msg_queue.append((log_message, self._clock()))

    def stop(self, graceful: bool = True):
        self._stopped = True
        if graceful:
            self._task.result()
        else:
            self._task.cancel()

    async def _loop_save(self):
        # This loop will run until the logger is stopped and the queue is empty
        while not self._stopped or (self._stopped and self._msg_queue):
            print(f"Queue size: {len(self._msg_queue)}", file=sys.stdout, flush=True)
            if self._msg_queue:
                msg = self._msg_queue.popleft()
                await self._write_to_file(msg)
            await asyncio.sleep(
                0.1
            )  # Avoids tight loop, adjustable based on expected log frequency
        return None

    async def _write_to_file(self, timed_msg: Tuple[str, datetime]):
        message, time = timed_msg
        log_file = self._get_file_handle(time)
        try:
            log_file.write(message + "\n")
            print(f"Logged: {message}", file=sys.stdout, flush=True)
        except IOError as e:
            print(e, file=sys.stderr, flush=True)

    # Assumes time is ever-increasing
    def _get_file_handle(self, time: datetime) -> TextIOWrapper:
        if (
            self._current_log_file is None
            or self._last_log_date is None
            or self._last_log_date != time.date()
        ):
            if self._current_log_file is not None:
                self._current_log_file.close()
            new_filename = time.strftime("%Y-%m-%d.log")
            self._current_log_file = open(
                self._logging_dir / new_filename, "a", encoding="utf-8"
            )
            self._last_log_date = time.date()
        return self._current_log_file
