import random

import app.settings as settings
from app.tasks import add
from flask import Flask, current_app, redirect, url_for
from redis import Redis
from rq import Queue

from judoscale.flask import Judoscale
from judoscale.rq import judoscale_rq

judoscale = Judoscale()


def publish_task(i=1):
    queue = "high" if random.random() > 0.5 else "low"
    current_app.logger.debug(f"Enqueuing a task on {queue=}")
    Queue(queue, connection=current_app.redis).enqueue(add, i, i)


def create_app():
    app = Flask("DemoFlaskApp")
    app.config.from_object(settings.BaseConfig)
    app.redis = Redis()

    judoscale.init_app(app)
    judoscale_rq(app.redis, extra_config=app.config.get("JUDOSCALE", {}))

    @app.get("/")
    def index():
        current_app.logger.warning("Hello, world")
        catcher_url = current_app.config["JUDOSCALE"]["API_BASE_URL"].replace(
            "/inspect/", "/p/"
        )
        return (
            "Judoscale RQ Sample App. "
            f"<a target='_blank' href={catcher_url}>Metrics</a>"
            "<form action='/task' method='POST'>"
            "<input type='submit' value='Add task'>"
            "</form>"
            "<form action='/batch_task' method='POST'>"
            "<input type='submit' value='Add 10 tasks'>"
            "</form>"
        )

    @app.post("/task")
    def task():
        publish_task()
        return redirect(url_for("index"))

    @app.post("/batch_task")
    def batch_task():
        for i in range(10):
            publish_task(i)
        return redirect(url_for("index"))

    return app


if __name__ == "__main__":
    create_app().run("127.0.0.1", "5000", debug=True)
