import threading
import time


class UtilizationTracker:
    """
    Tracks a count of active requests, incremented / decremented by the request
    middleware, and runs a separate thread that adds a "utilization" metric to
    the store, based on the process handling any requests or being idle.

    It pushes metrics directly to the underlying store, the same used by the
    WebMetricsCollector, which are them flushed and included with reports.
    """

    def __init__(self):
        self._active_request_counter = 0
        self._idle_started_at = None
        self._report_cycle_started_at = None
        self._total_idle_time = 0.0
        self._started = False
        self._lock = threading.Lock()

    @property
    def is_started(self):
        return self._started

    def start(self):
        with self._lock:
            if not self.is_started:
                self._started = True
                self._init_idle_report_cycle()

    def stop(self):
        with self._lock:
            if self.is_started:
                self._started = False
                self._idle_started_at = None
                self._report_cycle_started_at = None
                self._total_idle_time = 0.0
                self._active_request_counter = 0

    def incr(self):
        with self._lock:
            if self._active_request_counter == 0 and self._idle_started_at != None:
                # We were idle and now we're not - add to total idle time
                self._total_idle_time += (
                    self._get_current_time() - self._idle_started_at
                )
                self._idle_started_at = None

            self._active_request_counter += 1

    def decr(self):
        with self._lock:
            self._active_request_counter -= 1

            if self._active_request_counter == 0:
                # We're now idle - start tracking idle time
                self._idle_started_at = self._get_current_time()

    def utilization_pct(self, reset=True):
        with self._lock:
            current_time = self._get_current_time()
            idle_ratio = self._get_idle_ratio(current_time=current_time)

            if reset:
                self._reset_idle_report_cycle(current_time=current_time)

            return int((1.0 - idle_ratio) * 100.0)

    def _get_current_time(self):
        return time.monotonic()

    def _init_idle_report_cycle(self):
        current_time = self._get_current_time()
        self._idle_started_at = current_time
        self._reset_idle_report_cycle(current_time=current_time)

    def _reset_idle_report_cycle(self, current_time):
        self._total_idle_time = 0.0
        self._report_cycle_started_at = current_time

    def _get_idle_ratio(self, current_time):
        if self._report_cycle_started_at == None:
            return 0.0

        total_report_cycle_time = current_time - self._report_cycle_started_at

        if total_report_cycle_time <= 0:
            return 0.0

        # Capture remaining idle time
        if self._idle_started_at:
            self._total_idle_time += current_time - self._idle_started_at
            self._idle_started_at = current_time

        return self._total_idle_time / total_report_cycle_time


utilization_tracker = UtilizationTracker()
