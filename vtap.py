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
from components.my_args import parse_args
from components.ascii_picture import display_picture
from components.logger import log, print_log

class GracefulClose:
    kill_now = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.close)
        signal.signal(signal.SIGTERM, self.close)

    def exit_gracefully(self, signum, frame):
        self.kill_now = True

    def close(self, signum, frame):
        if self.kill_now:
            sys.exit(0)


@log('main')
def main():
    args = parse_args()
    
    shutdown_event = threading.Event()
    playback_started_event = threading.Event()

    def signal_handler(sig, frame):
        print("\nCtrl+C received. Gracefully closing...")
        shutdown_event.set()
        graceful_close = GracefulClose()
        print_log("Ctrl+C received. (signal_handler in vtap.py) Shutting down gracefully...", level='info')
        graceful_close.exit_gracefully(sig, frame)
        graceful_close.close(sig, frame)
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    if args.demo_picture:
        print("Demo mode enabled... you can use --chars to change the characters used to display the demo picture.")
        if not args.chars:
            args.chars = '█'
        args.image_path = 'https://cdn.computerhoy.com/sites/navi.axelspringer.es/public/media/image/2023/04/raspberry-lanza-editor-codigo-aprender-python-lenguaje-ia-3008158.jpg'
        print(f"This emulates running `python vtap.py --image_path {args.image_path} --chars {args.chars}`")
        time.sleep(2)

    if args.image_path:
        print(f"Playing image: {args.image_path} with character: {args.chars}")
        new_image_path = download_picture(args.image_path)
        display_picture(new_image_path, args, shutdown_event)
        sys.exit(0)

    if args.demo:
        print("Demo mode enabled... you can use --chars to change the characters used to display the demo video.")
        if not args.chars:
            args.chars = '█▓▒░ '
        args.url = 'https://www.youtube.com/watch?v=zyefOCRZMpA'
        print(f"This emulates running `python vtap.py --url {args.url} --chars {args.chars}`")
        time.sleep(2)

    if args.demo_two:
        print("Demo mode enabled... you can use --chars to change the characters used to display the demo video.")
        if not args.chars:
            args.chars = '█'
        args.url = 'https://www.youtube.com/watch?v=RvnxjeiVZ5Y'
        print(f"This emulates running `python vtap.py --url {args.url} --chars {args.chars}`")
        time.sleep(2)

    if not args.chars:
        args.chars = ' .:-=+*#%@'

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
        shutdown_event.set()
    
    video_thread.join()
    audio_thread.join()

if __name__ == '__main__':
    # find all log files in the app_logs directory and clear them
    log_files = Path('app_logs').glob('*.log')
    for log_file in log_files:
        clear_log = open(log_file, 'w')
        clear_log.write('')
        clear_log.close()
    main()
