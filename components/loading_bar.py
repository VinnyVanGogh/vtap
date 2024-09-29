# ./components/loading_bar.py

import sys
import os
import time

def display_loading_bar(total, processed_func, shutdown_event, refresh_interval=0.01):
    """
    Displays a loading bar in the console indicating the progress of preprocessing.

    Args:
        total (int): Total number of frames to process.
        processed_func (callable): Function that returns the current number of processed frames.
        shutdown_event (threading.Event): Event to signal shutdown.
        refresh_interval (float, optional): Time in seconds between updates. Defaults to 0.01.
    """
    while not shutdown_event.is_set():
        current = processed_func()
        percentage = (current / total) * 100 if total else 100
        max_bar_length = os.get_terminal_size().columns
        ten_percent = max_bar_length // 10 
        bar_length = max_bar_length - ten_percent
        filled_length = int(bar_length * current // total) if total else bar_length
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        sys.stdout.write(f'\r|{bar}| {percentage:.2f}%')
        sys.stdout.flush()
        if current >= total:
            break
        time.sleep(refresh_interval)
    sys.stdout.write('\n')
    sys.stdout.flush()
