import os

class Report:
    def __init__(self, metrics, config):
        self.metrics = metrics
        self.config = config

    def as_dict(self):
        metric_to_array = lambda m: [
            m.datetime.isoformat(),
            round(m.value, 2),
            m.measurement,
            m.queue_name,
        ]

        return {
            'dyno': self.config.dyno,
            'pid': os.getpid(),
            'config': self.config.as_dict(),
            'metrics': list(map(metric_to_array, self.metrics)),
        }
