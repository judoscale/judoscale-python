from unittest import mock

from judoscale.core.utilization_tracker import UtilizationTracker


class TestUtilizationTracker:
    def test_tracks_utilization_percentage_based_on_time_spent_with_no_active_requests(
        self,
    ):
        # T=0:   Start tracker
        # T=1:   Request 1 starts -> total_idle_time=1
        # T=2:   Request 1 ends   -> total_idle_time=1
        # T=4:   Request 2 starts -> total_idle_time=3 (1 + 2)
        # T=5:   Request 3 starts -> total_idle_time=3
        # T=6:   Request 2 ends   -> total_idle_time=3
        # T=8:   Request 3 ends   -> total_idle_time=3
        # T=10:  Report cycle     -> total_idle_time=5 (3 + 2), utilization_pct=50

        tracker = UtilizationTracker()

        # Stub time.monotonic to return our controlled monotonic time
        current_time = mock.Mock(return_value=0)
        with mock.patch("time.monotonic", current_time):
            # T=0: Tracker starts
            tracker.start()
            # No time has passed yet
            assert tracker.utilization_pct(reset=False) == 100

            # T=1: Request 1 starts
            current_time.return_value = 1
            tracker.incr()
            # 1 second idle out of 1 total second = 100% idle
            assert tracker.utilization_pct(reset=False) == 0

            # T=2: Request 1 ends
            current_time.return_value = 2
            tracker.decr()
            # 1 second idle out of 2 total seconds = 50% idle
            assert tracker.utilization_pct(reset=False) == 50

            # T=4: Request 2 starts
            current_time.return_value = 4
            tracker.incr()
            # 3 seconds idle out of 4 total seconds = 75% idle
            assert tracker.utilization_pct(reset=False) == 25

            # T=5: Request 3 starts
            current_time.return_value = 5
            tracker.incr()
            # 3 seconds idle out of 5 total seconds = 60% idle
            assert tracker.utilization_pct(reset=False) == 40

            # T=6: Request 2 ends
            current_time.return_value = 6
            tracker.decr()
            # 3 seconds idle out of 6 total seconds = 50% idle
            assert tracker.utilization_pct(reset=False) == 50

            # T=8: Request 3 ends
            current_time.return_value = 8
            tracker.decr()
            # 3 seconds idle out of 8 total seconds = 37.5% idle
            assert tracker.utilization_pct(reset=False) == 62

            # T=10: Report cycle - should calculate final utilization percentage
            current_time.return_value = 10
            # 5 seconds idle out of 10 total seconds = 50% idle
            assert tracker.utilization_pct() == 50

    def test_resets_the_tracking_cycle_when_utilization_pct_is_requested_with_no_args(
        self,
    ):
        # T=0:   Start tracker
        # T=1:   Request 1 starts -> total_idle_time=1
        # T=2:   Request 1 ends   -> total_idle_time=1
        # T=4:   Report cycle     -> total_idle_time=3 (1 + 2), utilization_pct=25
        # T=5:   Request 2 starts -> total_idle_time=1
        # T=8:   Report cycle     -> total_idle_time=1 (request still running), utilization_pct=75
        # T=9:   Request 3 starts -> total_idle_time=0
        # T=10:  Request 2 ends   -> total_idle_time=0
        # T=11:  Request 3 ends   -> total_idle_time=0
        # T=12:  Report cycle     -> total_idle_time=1, utilization_pct=75

        tracker = UtilizationTracker()

        # Stub time.monotonic to return our controlled monotonic time
        current_time = mock.Mock(return_value=0)
        with mock.patch("time.monotonic", current_time):
            # T=0: Tracker starts
            tracker.start()
            # No time has passed yet
            assert tracker.utilization_pct(reset=False) == 100

            # T=1: Request 1 starts
            current_time.return_value = 1
            tracker.incr()
            # 1 second idle out of 1 total second = 100% idle
            assert tracker.utilization_pct(reset=False) == 0

            # T=2: Request 1 ends
            current_time.return_value = 2
            tracker.decr()
            # 1 second idle out of 2 total seconds = 50% idle
            assert tracker.utilization_pct(reset=False) == 50

            current_time.return_value = 3
            # 2 seconds idle out of 3 total seconds = 66.66% idle
            assert tracker.utilization_pct(reset=False) == 33

            # T=4: Report cycle
            current_time.return_value = 4
            # 3 seconds idle out of 4 total seconds = 75% idle
            assert tracker.utilization_pct() == 25

            # T=5: Request 2 starts
            current_time.return_value = 5
            tracker.incr()
            # 1 second idle out of 1 total second = 100% idle
            assert tracker.utilization_pct(reset=False) == 0

            # T=8: Report cycle
            current_time.return_value = 8
            # 1 second idle out of 4 total seconds = 25% idle
            assert tracker.utilization_pct() == 75

            # T=9: Request 3 starts
            current_time.return_value = 9
            tracker.incr()
            # 0 seconds idle out of 1 total second = 0% idle
            assert tracker.utilization_pct(reset=False) == 100

            # T=10: Request 2 ends
            current_time.return_value = 10
            tracker.decr()
            # 0 seconds idle out of 2 total second = 0% idle
            assert tracker.utilization_pct(reset=False) == 100

            # T=11: Request 3 ends
            current_time.return_value = 11
            tracker.decr()
            # 0 seconds idle out of 3 total second = 0% idle
            assert tracker.utilization_pct(reset=False) == 100

            # T=12: Report cycle
            current_time.return_value = 12
            # 1 second idle out of 4 total seconds = 25% idle
            assert tracker.utilization_pct() == 75
