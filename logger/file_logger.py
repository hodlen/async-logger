from collections import deque
from pathlib import Path
from typing import Deque
from logger.base import ILog


class FileLogger(ILog):
    def __init__(self, logging_dir: Path) -> None:
        super().__init__()
        self._logging_dir = logging_dir
        self._stopped = False
        self._msg_queue: Deque[str] = deque()
        self._logging_dir.mkdir(parents=True, exist_ok=True)

    def write(self, log_message: str):
        if self._stopped:
            raise RuntimeError("Cannot write to a stopped logger.")
        self._msg_queue.append(log_message)

    def stop(self, graceful: bool = True):
        self._stopped = True

    def _loop_save(self):
        raise NotImplementedError("This method is not implemented yet.")
