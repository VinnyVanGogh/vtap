# ./components/ascii_video.py

import cv2
import os
import sys
import time
import threading
import queue
from colorama import init

from vtap.core import (
    AsciiArt,
    display_loading_bar,
    log,
    log_messages
)

@log('play_ascii_video')
def play_ascii_video(video_path, args, shutdown_event, playback_started_event):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if not fps or fps != fps:
        fps = 30  # Default to 30 FPS if not available
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

    @log('frame_reader')
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
            log_messages("exception", _func_name="frame_reader", _exception=e)
            shutdown_event.set()
        finally:
            cap.release()
            for _ in range(num_processor_threads):
                frame_queue.put(None)

    @log('frame_processor')
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

                log_messages("info", _message=f"Terminal size: {width}x{height}")

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
            log_messages("exception", _func_name="frame_processor", _exception=e)
            shutdown_event.set()

    @log('frame_display')
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
                try:
                    item = ascii_queue.get(timeout=0.1)
                except queue.Empty:
                    continue

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
            log_messages("exception", _func_name="frame_display", _exception=e)
            shutdown_event.set()
        finally:
            processing_done.set()
            total_msg = (
                f"Total frames processed: {total_frames_processed}\n"
                f"Total frames skipped: {total_frames_skipped}"
            )
            log_messages("info", _message=total_msg)

    reader_thread = threading.Thread(target=frame_reader, name="FrameReader")
    processor_threads = [
        threading.Thread(target=frame_processor, name=f"FrameProcessor-{i+1}")
        for i in range(num_processor_threads)
    ]

    start_time = time.time()
    reader_thread.start()
    for t in processor_threads:
        t.start()

    loading_bar_thread = threading.Thread(
        target=display_loading_bar,
        args=(initial_queue_size, get_processed_count, shutdown_event),
        name="LoadingBar"
    )

    loading_bar_thread.start()

    preprocessing_done.wait()
    loading_bar_thread.join()
    end_time = time.time()
    total_time = end_time - start_time
    avg_processing_time_per_frame = total_time / initial_queue_size

    log_messages(
        "info",
        _message=(
            f"Preprocessing {initial_queue_size} frames took {total_time:.2f} seconds.\n"
            f"Average processing time per frame: {avg_processing_time_per_frame:.4f} seconds.\n"
            f"Frame delay (time per frame at {fps} FPS): {frame_delay:.4f} seconds."
        )
    )

    estimated_skipped_frames = int((avg_processing_time_per_frame - frame_delay) * initial_queue_size)

    log_messages("info", _message=f"Estimated skipped frames: {estimated_skipped_frames}")

    if estimated_skipped_frames > 0:
        played_frames_per_skipped_frame = total_frames_processed / total_frames_skipped if total_frames_skipped else 0
        log_messages(
            "info",
            _message=(
                f"Played frames: {total_frames_processed}\n"
                f"Skipped frames: {total_frames_skipped}"
            )
        )
    else:
        log_messages("info", _message="No frames should be skipped.")

    if avg_processing_time_per_frame > frame_delay:
        log_messages("warning", _message="Processing is slower than the expected frame rate. Consider optimizing.")
    else:
        log_messages("info", _message="Processing is fast enough to keep up with the expected FPS.")

    playback_started_event.set()
    display_thread = threading.Thread(target=frame_display, name="FrameDisplay")
    display_thread.start()

    while not shutdown_event.is_set() and not processing_done.is_set():
        time.sleep(0.1)

    if shutdown_event.is_set():
        print('Video Shutdown event received. Exiting...')

    shutdown_event.set()

    reader_thread.join()
    for t in processor_threads:
        t.join()
    display_thread.join()

    log_credits()

