import rq.worker as rqw

from judoscale.rq import judoscale_rq


class JudoscaleRQWorkerMixin:
    def start_reporter(self: rqw.Worker, extra_config: dict = {}):
        judoscale_rq(self.connection, extra_config=extra_config)


class Worker(JudoscaleRQWorkerMixin, rqw.Worker):
    pass


class SimpleWorker(JudoscaleRQWorkerMixin, rqw.SimpleWorker):
    pass


class HerokuWorker(JudoscaleRQWorkerMixin, rqw.HerokuWorker):
    pass


class RoundRobinWorker(JudoscaleRQWorkerMixin, rqw.RoundRobinWorker):
    pass


class RandomWorker(JudoscaleRQWorkerMixin, rqw.RandomWorker):
    pass
