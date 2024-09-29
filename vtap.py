# vtap.py

import threading, signal, time, sys, os

from pathlib import Path

from components import (
        download_video,
        download_picture,
        play_ascii_video,
        play_audio,
        display_picture,
        demo_playbacks
        )

from core import (
        SignalHandler,
        clear_logs,
        log,
        print_log,
        kill_all_loggers 
        )

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
