import signal
import sys

from judoscale.core.reporter import reporter

previous_handler = signal.getsignal(signal.SIGTERM)

def graceful_shutdown(signum, frame):
    reporter.stop()
    # If there was a previous handler and it's not SIG_DFL or SIG_IGN, call it
    if callable(previous_handler) and previous_handler not in (
        signal.SIG_DFL,
        signal.SIG_IGN,
    ):
        previous_handler(signum, frame)
    else:
        # If no previous handler, use default behavior (exit the process)
        sys.exit(0)


signal.signal(signal.SIGTERM, graceful_shutdown)
