# ./components/my_args.py
# Example: python3.12 main.py --url https://www.youtube.com/watch?v=9bZkp7q19f0 -c " .:-=+*#%@"

import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Play YouTube video in ASCII art with audio.')
    parser.add_argument('-u','--url', help='YouTube video URL')
    parser.add_argument('-c','--chars', default=' .:-=+*#%@', help='Characters to use for ASCII art')
    parser.add_argument('-s','--scale', type=float, default=1.0, help='Scale factor for ASCII art (e.g., 0.5 for half size)')
    parser.add_argument('-co','--colors', action='store_true', default=True, help='Enable colored ASCII art')
    parser.add_argument('-fs','--fullscreen', action='store_true', default=True, help='Fit ASCII art to terminal size')
    parser.add_argument('-d', '--demo', action='store_true', default=False, help='Play a demo video')
    parser.add_argument('-i', '--image_path', default=None, help='Path to image file or url')

    return parser.parse_args()
