from datetime import datetime
from pathlib import Path

from logger import FileLogger


log_dir = Path("/tmp/async-logs")
mock_date = 1
mock_clock = lambda: datetime(2021, 1, mock_date)


def test_write_stop_ok():
    logger = FileLogger(log_dir)
    logger.write("Hello")
    logger.stop()


def test_write_content():
    logger = FileLogger(
        log_dir,
        logic_clock=mock_clock,
    )
    logger.write("Hello")
    logger.stop()
    with open(log_dir / "2021-01-01.log") as f:
        assert f.read() == "Hello\n"
