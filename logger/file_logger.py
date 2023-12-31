from datetime import date, datetime
from io import TextIOWrapper
from pathlib import Path
from queue import Queue
import sys
import threading
import time
from typing import Deque, Optional, Tuple
from logger.base import Clock, ILog


def _on_message_drop(msg: str, cause: Optional[Exception] = None):
    print(
        f"Message {msg} was dropped." + (" " + str(cause) if cause else ""),
        file=sys.stderr,
        flush=True,
    )


class FileLogger(ILog):
    _stopped = False
    _force_stop = False

    _logging_dir: Path
    _last_log_date: Optional[date] = None
    _current_log_file: Optional[TextIOWrapper] = None
    _clock: Clock = datetime.now

    def __init__(
        self,
        logging_dir: Path,
        logic_clock: Optional[Clock] = None,
        buffer_size: int = 1024,
        log_frequency_ms: int = 100,
        clock_override: Optional[Clock] = None,
    ):
        super().__init__()
        self._logging_dir = logging_dir
        self._logging_dir.mkdir(parents=True, exist_ok=True)
        self._msg_queue: Queue[Tuple[str, datetime]] = Queue(maxsize=buffer_size)
        self._log_frequency_ms = log_frequency_ms
        if clock_override is not None:
            self._clock = clock_override
        self._thread = threading.Thread(target=self._loop_save, daemon=True)
        self._thread.start()

    def write(self, log_message: str):
        if self._stopped:
            _on_message_drop(log_message)
        try:
            self._msg_queue.put_nowait((log_message, self._clock()))
        except Exception as e:
            _on_message_drop(log_message, e)

    def stop(self, graceful: bool = True):
        self._stopped = True
        if graceful:
            self._thread.join()
        else:
            self._force_stop = True

    def _loop_save(self):
        """This loop will run until the logger is stopped and the queue is empty (except for force stop)"""
        while not self._stopped or (
            self._stopped and not self._force_stop and not self._msg_queue.empty()
        ):
            pending_msg = [
                self._msg_queue.get_nowait() for _ in range(self._msg_queue.qsize())
            ]
            for msg in pending_msg:
                self._write_to_file(msg)
            time.sleep(
                self._log_frequency_ms / 1000
            )  # Avoids tight loop, adjustable based on expected log frequency
        if self._current_log_file is not None:
            self._current_log_file.close()

    def _write_to_file(self, timed_msg: Tuple[str, datetime]):
        message, time = timed_msg
        log_file = self._get_file_handle(time)
        try:
            log_file.write(message + "\n")
        except IOError as e:
            print(e, file=sys.stderr, flush=True)

    def _get_file_handle(self, time: datetime) -> TextIOWrapper:
        """
        Returns the file handle for the given time, creating a new file if necessary.
        Assmues time is ever-increasing.
        """
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
