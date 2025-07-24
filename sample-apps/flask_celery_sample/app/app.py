import random

import app.settings as settings
from app.tasks import add
from flask import Flask, current_app, redirect, url_for

from judoscale.flask import Judoscale

judoscale = Judoscale()


def publish_task(i=1):
    queue = "high" if random.random() > 0.5 else "low"
    current_app.logger.debug(f"Enqueuing a task on {queue=}")
    add.s(i, i).apply_async(queue=queue)


def create_app():
    app = Flask("DemoFlaskApp")
    app.config.from_object(settings.BaseConfig)
    judoscale.init_app(app)

    @app.get("/")
    def index():
        current_app.logger.warning("Hello, world")
        if url := current_app.config["JUDOSCALE"].get("API_BASE_URL"):
            return (
                "Judoscale Flask Celery Sample App. "
                f"<a target='_blank' href={url}>Metrics</a>"
                "<form action='/task' method='POST'>"
                "<input type='submit' value='Add task'>"
                "</form>"
                "<form action='/batch_task' method='POST'>"
                "<input type='submit' value='Add 10 tasks'>"
                "</form>"
            )
        else:
            return "Judoscale Flask Celery Sample App. No API URL provided."

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
