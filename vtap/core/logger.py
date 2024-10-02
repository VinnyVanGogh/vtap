# ./components/logger.py

import logging, contextvars, threading, os

from functools import wraps
from pathlib import Path

from vtap.core.signal_handling import SignalHandler

current_logger = contextvars.ContextVar('current_logger', default=None)

LOG_DIR = 'app_logs/'

loggers = {}

step_counter = 0

counter_lock = threading.Lock()

shutdown_event = SignalHandler().get_shutdown_event()

def kill_all_loggers():
    print("Killing and deleting all loggers to stop program.")
    for logger in loggers.values():
        for handler in logger.handlers:
            handler.close()
            logger.removeHandler(handler)
    loggers.clear()
    print("All loggers killed and deleted.", loggers)

def increment_step(shutdown_event):
    global step_counter
    with counter_lock:
        if not shutdown_event.is_set():
            step_counter += 1
        return step_counter

def get_logger(log_file):
    if not Path(LOG_DIR).exists():
        Path(LOG_DIR).mkdir()
    log_file = LOG_DIR + log_file
    if not log_file.endswith('.log'):
        log_file += '.log'

    if log_file not in loggers:
        logger = logging.getLogger(log_file)
        logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.propagate = False
        loggers[log_file] = logger
    return loggers[log_file]

def log(log_file):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(log_file)
            current_step = increment_step(shutdown_event)
            token = current_logger.set(logger)
            try:
                logger.debug(f"Step {current_step}: Called function '{func.__name__}'")
                logger.debug(f"Args for {func.__name__}: {args}, kwargs: {kwargs}")
                result = func(*args, **kwargs)
                logger.debug(f"Function '{func.__name__}' returned: {result}")
                return result
            except Exception as e:
                logger.exception(f"Exception in function '{func.__name__}': {e}")
                raise
            finally:
                current_logger.reset(token)
        return wrapper
    return decorator

def print_log(message, level='INFO'):
    logger = current_logger.get()
    if not logger:
        logger = get_logger('main')
    if logger:

        if level.upper() == 'DEBUG':
            logger.debug(message)
        elif level.upper() == 'INFO':
            logger.info(message)
        elif level.upper() == 'WARNING':
            logger.warning(message)
        elif level.upper() == 'ERROR':
            logger.error(message)
        elif level.upper() == 'CRITICAL':
            logger.critical(message)
        else:
            logger.info(message)
    else:
        raise RuntimeError("print_log called outside of a decorated function. No logger is set.")

def clear_logs():
    log_files = Path('app_logs').glob('*.log')
    for log_file in log_files:
        clear_log = open(log_file, 'w')
        clear_log.write('')
        clear_log.close()
