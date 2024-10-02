# ./components/loading_bar.py

import sys, os, time

from vtap.core.logger import log

@log('main')
def display_loading_bar(total, processed_func, shutdown_event, refresh_interval=0.01):
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

