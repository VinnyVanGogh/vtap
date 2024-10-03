# vtap.py

import threading
import time
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed


from vtap.components import *
from vtap.core import *

@log('main')
def run_program(shutdown_event):
    active_processes = ActiveProcesses()
    max_cores = os.cpu_count()
    max_workers = max_cores - 2 if max_cores > 2 else 1
    executor = ThreadPoolExecutor(max_workers=max_workers)
    ThreadKiller(active_processes, executor)
    playback_started_event = threading.Event()

    args = demo_playbacks()

    print(f'Arguments: {args}')

    if args.image_path:
        new_image_path = download_picture(args.image_path)
        display_picture(new_image_path, args, shutdown_event)
        sys.exit(0)

    video_path = download_video(args.url)

    video_thread = threading.Thread(
        target=play_ascii_video,
        args=(video_path, args, shutdown_event, playback_started_event)
    )
    audio_thread = threading.Thread(
        target=play_audio,
        args=(video_path, shutdown_event)
    )

    video_thread.start()
    playback_started_event.wait()
    audio_thread.start()

    try:
        while video_thread.is_alive() or audio_thread.is_alive():
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nCtrl+C received... Shutting down gracefully...")
        print(shutdown_event.is_set())
        video_thread.join()
        audio_thread.join()
        kill_all_loggers()
        shutdown_event.set()
        sys.exit(0)
    
    video_thread.join()
    audio_thread.join()


@log('main')
def main():
    shutdown_event = SignalHandler().get_shutdown_event()
    
    SignalHandler().set_signal_handler()

    clear_logs()
    run_program(shutdown_event)

if __name__ == '__main__':
    main()
