# ./components/demo_setup.py 

import time
from core.my_args import parse_args
from core.logger import log, print_log

@log('main')
def demo_playbacks():
    args = parse_args()
    if args.demo_picture:
        print("Demo mode enabled... you can use --chars to change the characters used to display the demo picture.")
        if not args.chars:
            args.chars = '█'
        args.image_path = 'https://cdn.computerhoy.com/sites/navi.axelspringer.es/public/media/image/2023/04/raspberry-lanza-editor-codigo-aprender-python-lenguaje-ia-3008158.jpg'
        print(f"This emulates running `python vtap.py --image_path {args.image_path} --chars {args.chars}`")
        time.sleep(2)

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

    return args
