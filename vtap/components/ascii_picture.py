# ./components/ascii_picture.py

import cv2
import os
import time

from vtap.core import (
        AsciiArt,
        log,
        print_log
    )

@log('main')
def display_picture(new_image_path, args, shutdown_event):
    try:
        frame = cv2.imread(new_image_path)
        if frame is None:
            print_log(f"Failed to load image: {new_image_path}", level='INFO')
            return

        term_size = os.get_terminal_size()
        width, height = term_size.columns, term_size.lines

        if not args.fullscreen:
            width = int(width * args.scale)
            height = int(height * args.scale)

        ascii_art_generator = AsciiArt(args, frame, (width, height))
        ascii_frame = ascii_art_generator.ascii_art()

        if os.name == 'nt':
            os.system('')
        print('\033[2J', end='')
        print('\033[?25l', end='')

        print('\033[H', end='')
        print(ascii_frame, end='', flush=True)

        while not shutdown_event.is_set():
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nCtrl+C received in ascii_picture.py. Shutting down gracefully...")
        print_log("Ctrl+C received in ascii_picture.py. Shutting down gracefully...")
        shutdown_event.set()
    finally:
        print('\033[?25h', end='')
