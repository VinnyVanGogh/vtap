# ./components/ascii_video.py

import cv2, os, sys, time, threading, queue
from colorama import init, Style

from core.ascii_art import AsciiArt
from core.signal_handling import SignalHandler

from components.logger import log, print_log
from components.loading_bar import display_loading_bar

@log('main')
def play_ascii_video(video_path, args, shutdown_event, playback_started_event):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if not fps or fps != fps:
        fps = 30  # Default to 30 FPS if not available (average for most videos)
    frame_delay = 1 / fps

    term_size = os.get_terminal_size() 
    width, height = term_size.columns, term_size.lines
    if not args.fullscreen:
        width = int(width * args.scale)
        height = int(height * args.scale)

    init()

    processing_done = threading.Event()

    num_processor_threads = os.cpu_count() or 4

    initial_queue_size = 120
    frame_queue = queue.Queue(maxsize=initial_queue_size)
    ascii_queue = queue.Queue(maxsize=initial_queue_size)
    total_frames_processed = 0
    total_frames_skipped = 0
    frame_number = 0

    preprocessing_done = threading.Event()

    total_processed_count = [0]
    processed_count_lock = threading.Lock()
    def get_processed_count():
        with processed_count_lock:
            return total_processed_count[0]

    @log('ascii_display')
    def frame_reader():
        nonlocal frame_number
        try:
            while not shutdown_event.is_set():
                ret, frame = cap.read()
                if not ret:
                    break
                frame_number += 1
                frame_queue.put((frame_number, frame))
        except Exception as e:
            print(f"Exception in frame_reader: {e}")
            print_log(f"Exception in frame_reader: {e}", level="error")
        finally:
            cap.release()
            for _ in range(num_processor_threads):
                frame_queue.put(None)

    @log('ascii_processor')
    def frame_processor():
        try:
            while not shutdown_event.is_set():
                item = frame_queue.get()
                if item is None:
                    ascii_queue.put(None)
                    break
                f_number, frame = item

                term_size = os.get_terminal_size()
                width, height = term_size.columns, term_size.lines
                if not args.fullscreen:
                    width = int(width * args.scale)
                    height = int(height * args.scale)
    
                print_log(f"Terminal size: {width}x{height}", level="info")

                start_time = time.time()
                ascii_art_generator = AsciiArt(args, frame, (width, height))
                ascii_frame = ascii_art_generator.ascii_art()
                processing_time = time.time() - start_time

                ascii_queue.put((f_number, ascii_frame))

                with processed_count_lock:
                    total_processed_count[0] += 1
                    if total_processed_count[0] == initial_queue_size:
                        preprocessing_done.set()
        except Exception as e:
            print(f"Exception in frame_processor: {e}")
            print_log(f"Exception in frame_processor: {e}", level="error")

    @log('ascii_display')
    def frame_display():
        nonlocal total_frames_processed, total_frames_skipped
        expected_frame_time = time.time()
        try:
            if os.name == 'nt':
                os.system('')
            print('\033[2J', end='')
            print('\033[?25l', end='')
            sys.stdout.flush()

            playback_started_event.set()

            while not shutdown_event.is_set():
                item = ascii_queue.get()
                if item is None:
                    break
                f_number, ascii_frame = item

                current_time = time.time()
                time_diff = current_time - expected_frame_time

                if time_diff > 0:
                    frames_behind = int(time_diff / frame_delay)
                    expected_frame_time += (frames_behind + 1) * frame_delay
                    total_frames_skipped += frames_behind

                else:
                    expected_frame_time += frame_delay

                total_frames_processed += 1

                print('\033[H', end='')
                print(ascii_frame, end='', flush=True)

                sleep_time = expected_frame_time - time.time()
                if sleep_time > 0:
                    time.sleep(sleep_time)

            print('\033[?25h', end='')
            sys.stdout.flush()

        except Exception as e:
            print(f"Exception in frame_display: {e}")
            print_log(f"Exception in frame_display: {e}", level="error")
        finally:
            processing_done.set()
            print_log(f"Total frames processed: {total_frames_processed}", level="info")
            print_log(f"Total frames skipped: {total_frames_skipped}", level="warning")

    reader_thread = threading.Thread(target=frame_reader)
    processor_threads = [threading.Thread(target=frame_processor) for _ in range(num_processor_threads)]

    start_time = time.time()
    reader_thread.start()
    for t in processor_threads:
        t.start()

    loading_bar_thread = threading.Thread(
        target=display_loading_bar,
        args=(initial_queue_size, get_processed_count, shutdown_event),
        daemon=False
    )

    loading_bar_thread.start()

    preprocessing_done.wait()
    loading_bar_thread.join()
    end_time = time.time()
    total_time = end_time - start_time
    avg_processing_time_per_frame = total_time / initial_queue_size

    print_log(f"Preprocessing {initial_queue_size} frames took {total_time:.2f} seconds.", level="info")
    print_log(f"Average processing time per frame: {avg_processing_time_per_frame:.4f} seconds.", level="info")
    print_log(f"Frame delay (time per frame at {fps} FPS): {frame_delay:.4f} seconds.", level="info")

    estimated_skipped_frames = int((avg_processing_time_per_frame - frame_delay) * initial_queue_size)
    
    print_log(f"Estimated skipped frames: {estimated_skipped_frames}", level="warning")
    
    if estimated_skipped_frames > 0:
        played_frames_per_skipped_frame = total_frames_processed / total_frames_skipped
        print_log(f"Played frames per skipped frame: {played_frames_per_skipped_frame:.2f}", level="warning")
    else:
        print_log("No frames should be skipped.", level="info")

    if avg_processing_time_per_frame > frame_delay:
        print_log("Warning: Processing is slower than the expected frame rate. Consider optimizing.", level="warning")
    else:
        print_log("Processing is fast enough to keep up with the expected FPS.", level="info")

    playback_started_event.set()
    display_thread = threading.Thread(target=frame_display)
    display_thread.start()

    while not shutdown_event.is_set() and not processing_done.is_set():
        time.sleep(0.1)
    shutdown_event = SignalHandler().get_shutdown_event()

    if shutdown_event.is_set():
        print('Video Shutdown event received. Exiting...')

    shutdown_event.set()

    reader_thread.join()
    for t in processor_threads:
        t.join()
    display_thread.join()

    print_log("Video playback complete.", level="info")
    print_log(f"Total frames processed: {total_frames_processed}", level="info")
