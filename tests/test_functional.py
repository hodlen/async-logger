from pathlib import Path

from logger import FileLogger


log_dir = Path("/tmp/async-logs")


def test_write_stop_ok():
    logger = FileLogger(log_dir)
    logger.write("Hello")
    logger.stop()
