# ./core/ascii_art.py

import cv2
import numpy as np
from colorama import init

from core.logger import log, print_log

init()

class AsciiArt:

    @log('ascii_art')
    def __init__(self, args, frame, frame_size):
        self.args = args
        self.frame = frame
        self.frame_size = frame_size
        self.chars = np.array(list(args.chars))
        self.num_chars = len(self.chars)
        self.area = 255 // (self.num_chars - 1) if self.num_chars > 1 else 255

    @log('ascii_art')
    def ascii_art(self):
        resized_frame = cv2.resize(self.frame, self.frame_size, interpolation=cv2.INTER_AREA)

        gray_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)

        char_indices = (gray_frame // self.area) % self.num_chars
        ascii_chars = self.chars[char_indices]

        if self.args.colors:
            rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
            ascii_chars_flat = ascii_chars.flatten()
            rgb_frame_flat = rgb_frame.reshape(-1, 3)

            colored_chars = np.array([
                f'\033[38;2;{r};{g};{b}m{char}\033[0m'
                for char, (r, g, b) in zip(ascii_chars_flat, rgb_frame_flat)
            ])

            colored_chars = colored_chars.reshape(ascii_chars.shape)

            ascii_image = '\n'.join([''.join(row) for row in colored_chars])
        else:
            ascii_image = '\n'.join([''.join(row) for row in ascii_chars])

        return ascii_image
