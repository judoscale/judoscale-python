from judoscale.core.reporter import Reporter
from judoscale.core.metric import Metric
from datetime import datetime

class TestReporter:
    def test_build_report(self):
        reporter = Reporter()
        dt = datetime.fromisoformat("2012-12-12T12:12:00+00:00")
        metric = Metric(measurement="test", datetime=dt, value=123)

        report = reporter._build_report([metric])

        assert list(report.keys()).sort() == ['config', 'dyno', 'pid', 'metrics'].sort()
        assert len(report['metrics']) == 1
        assert report['metrics'][0] == [1355314320, 123, "test", None]
