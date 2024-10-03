# vtap.py

import threading
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from vtap.components import *
from vtap.core import *

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

@log('main')
def run_program(shutdown_event):
    active_processes = ActiveProcesses()
    max_cores = os.cpu_count()
    max_workers = max_cores - 2 if max_cores > 2 else 1
    executor = ThreadPoolExecutor(max_workers=max_workers)
    ThreadKiller(active_processes, executor)
    playback_started_event = threading.Event()

    args = demo_playbacks()
    clear_terminal()

    if args.image_path:
        new_image_path = download_picture(args.image_path)
        display_picture(new_image_path, args, shutdown_event)
        sys.exit(0)

    video_path = download_video(args.url)

    video_thread = executor.submit(
        play_ascii_video,
        video_path, args, shutdown_event, playback_started_event
    )

    audio_thread = executor.submit(
        play_audio,
        video_path
    )

    audio_future = executor.submit(
        play_audio,
        video_path, active_processes, shutdown_event  # Pass active_processes and shutdown_event
    )

    video_future = executor.submit(
        play_ascii_video,
        video_path, args, shutdown_event, playback_started_event, active_processes  # Pass active_processes
    )

    try:
        # Wait for both tasks to complete
        for future in as_completed([video_future, audio_future]):
            pass
    except KeyboardInterrupt:
        print("\nCtrl+C received... Shutting down gracefully...")
        shutdown_event.set()
        kill_all_loggers()
        sys.exit(0)

    # Shutdown the executor
    executor.shutdown(wait=True)

@log('main')
def main():
    shutdown_event = SignalHandler().get_shutdown_event()
    
    SignalHandler().set_signal_handler()

    clear_logs()
    run_program(shutdown_event)

