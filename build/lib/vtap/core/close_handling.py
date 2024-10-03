import threading 
import signal 
import sys 
import os

BOLD = "\033[1m"
END = "\033[0m"
ORANGE = "\033[33m"
LINK = "\033[4m"

class GracefulClose:
    kill_now = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.close)
        signal.signal(signal.SIGTERM, self.close)

    def exit_gracefully(self, signum, frame):
        self.kill_now = True

    def close(self, signum, frame):
        self.exit_gracefully(signum, frame)
        # if self.kill_now:
        #     sys.exit(0)

class ActiveProcesses:
    def __init__(self):
        self.processes = []
        self.lock = threading.Lock()

class ThreadKiller:
    def __init__(self, active_processes, executor):
        self.active_processes = active_processes
        self.executor = executor
        self.shutdown_event = threading.Event()
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)

    def handle_signal(self, signum, frame):
        print(f"{BOLD}Received interrupt signal. Shutting down gracefully...{END}\n")
        self.shutdown_event.set()
        self.terminate_processes()
        self.executor.shutdown(wait=False)
        sys.exit(0)

    def terminate_processes(self):
        print(f"{BOLD}Terminating all active subprocesses...{END}\n")
        with self.active_processes.lock:
            for proc in self.active_processes.processes:
                if proc.poll() is None:
                    print(f"{ORANGE}Terminating subprocess with PID {proc.pid}...{END}")
                    proc.terminate()
                    try:
                        if os.name == 'nt':
                            proc.send_signal(signal.CTRL_BREAK_EVENT)
                        else:
                            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                    except Exception as e:
                        print(f"Error terminating subprocess: {e}")
            self.active_processes.processes.clear()
