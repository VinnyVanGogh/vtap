import signal 
import threading 
from core.close_handling import GracefulClose

class SignalHandler:
    def __init__(self):
        self.shutdown_event = threading.Event()

    def signal_handler(self, sig, frame):
        print("\nCtrl+C received. Gracefully closing...")
        graceful_close = GracefulClose()
        graceful_close.exit_gracefully(sig, frame)
        graceful_close.close(sig, frame)
        self.shutdown_event.set()

    def set_signal_handler(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def get_shutdown_event(self):
        return self.shutdown_event
