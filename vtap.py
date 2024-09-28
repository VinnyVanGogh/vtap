# vtap.py

import threading
import signal
import time
import sys
from components.downloader import download_video, download_picture
from components.ascii_video import play_ascii_video
from components.audio_player import play_audio
from components.my_args import parse_args
from components.ascii_picture import display_picture

def main():
    args = parse_args()
    
    shutdown_event = threading.Event()
    playback_started_event = threading.Event()

    def signal_handler(sig, frame):
        print("\nCtrl+C received. Shutting down gracefully...")
        shutdown_event.set()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    if args.image_path:
        print(f"Playing image: {args.image_path} with character: {args.chars}")
        new_image_path = download_picture(args.image_path)
        display_picture(new_image_path, args, shutdown_event)
        sys.exit(0)

    if args.demo:
        print("Demo mode enabled...")
        args.chars = '█'
        args.url = 'https://www.youtube.com/watch?v=zyefOCRZMpA'
        print(f"Playing video: {args.url} with character: {args.chars}")
        time.sleep(2)
    
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
    # Wait until the video playback is about to start
    playback_started_event.wait()
    audio_thread.start()

    try:
        while video_thread.is_alive() or audio_thread.is_alive():
            time.sleep(0.1)
    except KeyboardInterrupt:
        shutdown_event.set()
        print("\nKeyboardInterrupt received. Shutting down...")
    
    video_thread.join()
    audio_thread.join()

if __name__ == '__main__':
    main()

