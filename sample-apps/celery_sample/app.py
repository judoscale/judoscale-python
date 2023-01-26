import random
import time

import settings
from celery import Celery
from flask import Flask, current_app, redirect, url_for

from judoscale.celery import judoscale_celery
from judoscale.flask import Judoscale

judoscale = Judoscale()
celery = Celery("DemoCeleryApp", broker="redis://localhost:6379/0")


@celery.task
def add(x, y):
    time.sleep(random.randint(3, 5))
    return x + y


def create_app():
    app = Flask("DemoFlaskApp")
    app.config.from_object(settings.BaseConfig)
    judoscale.init_app(app)

    judoscale_celery(celery, extra_config=app.config.get("JUDOSCALE", {}))

    @app.get("/")
    def index():
        current_app.logger.warning("Hello, world")
        catcher_url = current_app.config["JUDOSCALE"]["API_BASE_URL"]
        return (
            "Judoscale Flask Sample App. "
            f"<a target='_blank' href={catcher_url}>Metrics</a>"
            "<form action='/task' method='POST'>"
            "<input type='submit' value='Add task'>"
            "</form>"
        )

    @app.post("/task")
    def task():
        add.s(1, 2).apply_async(queue="celery" if random.random() > 0.5 else "foobar")
        return redirect(url_for("index"))

    return app


if __name__ == "__main__":
    create_app().run("127.0.0.1", "5000", debug=True)
