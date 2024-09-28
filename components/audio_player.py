# ./components/audio_player.py

import subprocess
import os
import sys
import threading
import time
import signal
from components.logger import log, print_log

@log('main')
def play_audio(video_path, shutdown_event):
    cmd = [
        'ffplay', '-nodisp', '-autoexit', '-loglevel', 'quiet', video_path
    ]

    try:
        if os.name == 'nt':
            process = subprocess.Popen(cmd, shell=True, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        else:
            process = subprocess.Popen(cmd, preexec_fn=os.setsid)
        
        while not shutdown_event.is_set():
            time.sleep(0.1)
            if process.poll() is not None:
                break
    except Exception as e:
        print(f"Exception in play_audio: {e}")
        print_log(f"Exception in play_audio: {e}", level='error')
    finally:
        if shutdown_event.is_set():
            print("Terminating audio subprocess")
            if process.poll() is None:
                try:
                    if os.name == 'nt':
                        process.send_signal(subprocess.CTRL_BREAK_EVENT)
                    else:
                        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                except Exception as e:
                    print(f"Error terminating audio subprocess: {e}")
                    print_log(f"Error terminating audio subprocess: {e}", level='error')
        process.wait()
