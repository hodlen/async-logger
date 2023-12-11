# async-logger

## Overview

async-logger is a Python logging module designed for asynchronous logging. It leverages threading for efficient log handling and offers features like batch processing, graceful and forced shutdown, and automatic file rotation based on dates.

## Features

- **Asynchronous Logging:** Utilizes Python threading to ensure non-blocking log writes.
- **Queue-Based Batch Processing:** Enhances performance by processing log messages in batches.
- **Automatic File Rotation:** Daily log file rotation to organize log entries.
- **Graceful and Immediate Shutdown:** Supports both orderly shutdown and immediate termination.

## Implementation

- **Threading:** A daemon thread is used for log processing, separating the logging concern from the main application flow.
- **Batched Log Processing:** Handles all messages in the queue at once, minimizing thread context-switching.
- **Error Handling:** Logs file writing errors to `sys.stderr`, ensuring application continuity.

## Usage

```python
from FileLogger import FileLogger
from pathlib import Path

# Initialize the logger
logger = FileLogger(logging_dir=Path('./logs'))

# Write a log message
logger.write("Sample log message")

# Stop the logger
logger.stop(graceful=True)
```

## Notes

- **Threading vs. asyncio:** Chosen for compatibility with synchronous environments, avoiding the complexities of mixing sync and async code.
- **Performance Considerations:** Batch processing in threading reduces overhead, making it suitable for high-load scenarios.
