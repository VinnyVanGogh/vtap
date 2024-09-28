# vtap.py

import threading
import signal
import time
import sys
from pathlib import Path
from components.downloader import download_video, download_picture
from components.ascii_video import play_ascii_video
from components.audio_player import play_audio
from components.my_args import parse_args
from components.ascii_picture import display_picture
from components.logger import log, print_log

@log('main')
def main():
    args = parse_args()
    
    shutdown_event = threading.Event()
    playback_started_event = threading.Event()

    @log('main')
    def signal_handler(sig, frame):
        print("\nCtrl+C received. Shutting down gracefully...")
        print_log('Ctrl+C received. Shutting down gracefully...', level='INFO')
        shutdown_event.set()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    if args.demo_picture:
        print("Demo mode enabled...")
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
        print("Demo mode enabled...")
        if not args.chars:
            args.chars = '█▓▒░ '
        args.url = 'https://www.youtube.com/watch?v=zyefOCRZMpA'
        print(f"This emulates running `python vtap.py --url {args.url} --chars {args.chars}`")
        time.sleep(2)

    if args.demo_two:
        print("Demo mode enabled...")
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
        shutdown_event.set()
        print("\nKeyboardInterrupt received. Shutting down...")
        print_log('KeyboardInterrupt received. Shutting down...', level='INFO')
    
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

