# ./components/logger.py

import logging
from functools import wraps
import contextvars
from pathlib import Path
import threading

current_logger = contextvars.ContextVar('current_logger', default=None)

Path('app_logs').mkdir(parents=True, exist_ok=True)

LOG_DIR = 'app_logs/'

loggers = {}

step_counter = 0
counter_lock = threading.Lock()

def increment_step():
    global step_counter
    with counter_lock:
        step_counter += 1
        return step_counter

def get_logger(log_file):
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
            current_step = increment_step()
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
    if logger:
        current_step = step_counter

        if level.upper() == 'DEBUG':
            logger.debug(message, extra={'step': current_step})
        elif level.upper() == 'INFO':
            logger.info(message, extra={'step': current_step})
        elif level.upper() == 'WARNING':
            logger.warning(message, extra={'step': current_step})
        elif level.upper() == 'ERROR':
            logger.error(message, extra={'step': current_step})
        elif level.upper() == 'CRITICAL':
            logger.critical(message, extra={'step': current_step})
        else:
            logger.info(message, extra={'step': current_step})
    else:
        raise RuntimeError("print_log called outside of a decorated function. No logger is set.")
