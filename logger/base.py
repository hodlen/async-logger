from abc import ABC, abstractmethod
from datetime import datetime
from typing import Callable


class ILog(ABC):
    @abstractmethod
    def write(self, log_message: str):
        """
        Asynchronously writes a log message to the log.
        :param log_message: The message to be logged.
        """
        pass

    @abstractmethod
    def stop(self, graceful: bool = True):
        """
        Stops the logging process.
        :param graceful: If True, gracefully shut down by finishing pending log messages.
                         If False, shut down immediately.
        """
        pass


Clock = Callable[[], datetime]
