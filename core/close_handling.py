import sys
import signal

class GracefulClose:
    kill_now = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.close)
        signal.signal(signal.SIGTERM, self.close)

    def exit_gracefully(self, signum, frame):
        self.kill_now = True

    def close(self, signum, frame):
        self.exit_gracefully(signum, frame)
        if self.kill_now:
            sys.exit(0)
