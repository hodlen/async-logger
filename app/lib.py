from pathlib import Path
import time
from logger.file_logger import FileLogger


def count_time_elapsed(timeout_secs: int):
    """Log the seconds passed"""
    logger = FileLogger(Path("/tmp/logs"))
    for i in range(1, timeout_secs + 1):
        time.sleep(1)
        logger.write(f"Time elapsed: {i} seconds")

    logger.stop()
