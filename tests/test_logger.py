from datetime import datetime
from os import system
from pathlib import Path

import pytest

from logger import FileLogger


mock_date = 1
mock_clock = lambda: datetime(2021, 1, mock_date)
log_dir = Path("/tmp/async-logs")


@pytest.fixture(autouse=True)
def run_before_and_after_tests(tmpdir):
    """Fixture to execute asserts before and after a test is run"""
    yield  # Run test
    system(f"rm -rf {log_dir}")  # Teardown


def test_write_stop_ok():
    logger = FileLogger(log_dir)
    logger.write("Hello")
    logger.stop()


def test_force_stop_ok():
    logger = FileLogger(log_dir)
    logger.write("Hello")
    logger.stop(graceful=False)


def test_write_content():
    logger = FileLogger(
        log_dir,
        logic_clock=mock_clock,
    )
    logger.write("Hello")
    logger.stop()
    with open(log_dir / "2021-01-01.log") as f:
        assert f.read() == "Hello\n"


def test_file_rotation():
    global mock_date
    logger = FileLogger(
        log_dir,
        logic_clock=mock_clock,
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
    global mock_date
    logger = FileLogger(
        log_dir,
        logic_clock=mock_clock,
    )
    for d in range(1, 10):
        print("Day", d)
        for i in range(10**3):
            logger.write(f"Hello {i}")
    logger.stop()
    for d in range(1, 30):
        with open(log_dir / f"2021-01-{d:02d}.log") as f:
            assert len(f.readlines()) == 10**3
