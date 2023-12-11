from datetime import datetime
from os import system
from pathlib import Path
import time

import pytest

from logger import FileLogger


mock_date = 1
mock_clock = lambda: datetime(2021, 1, mock_date)
log_dir = Path("/tmp/async-logs")


@pytest.fixture(autouse=True)
def run_before_and_after_tests(tmpdir):
    """Fixture to execute asserts before and after a test is run"""
    global mock_date
    mock_date = 1  # Setup
    yield  # Run test
    system(f"rm -rf {log_dir}")  # Teardown


def test_write_stop_ok():
    logger = FileLogger(log_dir)
    logger.write("Hello")
    logger.stop()


def test_force_stop_ok():
    logger = FileLogger(log_dir)
    logger.write("Hello")
    before_stop = datetime.now()
    logger.stop(graceful=False)
    # Assert that the stop was immediate
    assert (datetime.now() - before_stop).microseconds < 100


def test_write_content():
    logger = FileLogger(
        log_dir,
        clock_override=mock_clock,
    )
    logger.write("Hello")
    logger.stop()
    with open(log_dir / "2021-01-01.log") as f:
        assert f.read() == "Hello\n"


def test_file_rotation():
    global mock_date
    logger = FileLogger(
        log_dir,
        clock_override=mock_clock,
    )
    logger.write("Hello")
    mock_date += 1
    logger.write("World")
    logger.stop()
    with open(log_dir / "2021-01-01.log") as f:
        assert f.read() == "Hello\n"
    with open(log_dir / "2021-01-02.log") as f:
        assert f.read() == "World\n"


def test_performance():
    """Under extreme load, the logger should not drop messages over 1%"""

    global mock_date
    logger = FileLogger(
        log_dir,
        clock_override=mock_clock,
        log_frequency_ms=0,
    )
    for d in range(1, 10):
        print("Day", d)
        for i in range(10**6):
            logger.write(f"Hello {i}")
        mock_date += 1

    logger.stop()
    for d in range(1, 10):
        with open(log_dir / f"2021-01-{d:02d}.log") as f:
            assert len(f.readlines()) >= 10**6 * 0.99
