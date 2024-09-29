# vtap.py

import threading
import signal
import time
import sys
import os
from pathlib import Path
from components.downloader import download_video, download_picture
from components.ascii_video import play_ascii_video
from components.audio_player import play_audio
from components.ascii_picture import display_picture

from core.logger import log, print_log, kill_all_loggers

from components.demo_setup import demo_playbacks
from core.signal_handling import SignalHandler



@log('main')
def run_program(shutdown_event):
    playback_started_event = threading.Event()

    args = demo_playbacks()

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
        print("\nCtrl+C received. (main in vtap.py) Shutting down gracefully...")
        print(shutdown_event.is_set())
        video_thread.join()
        audio_thread.join()
        kill_all_loggers()
        shutdown_event.set()
        sys.exit(0)
    
    video_thread.join()
    audio_thread.join()

def clear_logs():
    log_files = Path('app_logs').glob('*.log')
    for log_file in log_files:
        clear_log = open(log_file, 'w')
        clear_log.write('')
        clear_log.close()

def main():
    clear_logs()

    shutdown_event = SignalHandler().get_shutdown_event()
    SignalHandler().set_signal_handler()

    run_program(shutdown_event)

if __name__ == '__main__':
    main()
