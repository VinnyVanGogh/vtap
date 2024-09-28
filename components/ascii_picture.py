# ./components/ascii_picture.py

import cv2
import os
import sys
import time
import threading
from components.ascii_art import AsciiArt

def display_picture(new_image_path, args, shutdown_event):
    try:
        # Read the image
        frame = cv2.imread(new_image_path)
        if frame is None:
            print(f"Failed to load image: {new_image_path}")
            return

        # Get terminal size
        term_size = os.get_terminal_size()
        width, height = term_size.columns, term_size.lines

        # Adjust height to account for character aspect ratio
        # aspect_ratio_correction = 0.55  # Adjust this value as needed
        # height = int(height * aspect_ratio_correction)

        if not args.fullscreen:
            width = int(width * args.scale)
            height = int(height * args.scale)

        # Generate ASCII art
        ascii_art_generator = AsciiArt(args, frame, (width, height))
        ascii_frame = ascii_art_generator.ascii_art()

        # Prepare terminal for display
        if os.name == 'nt':
            os.system('')
        print('\033[2J', end='')  # Clear screen
        print('\033[?25l', end='')  # Hide cursor

        # Display ASCII art
        print('\033[H', end='')  # Move cursor to top-left
        print(ascii_frame, end='', flush=True)

        # Wait for user to press Enter or shutdown event
        while not shutdown_event.is_set():
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nCtrl+C received. Shutting down gracefully...")
        shutdown_event.set()
    finally:
        print('\033[?25h', end='')  # Show cursor again

