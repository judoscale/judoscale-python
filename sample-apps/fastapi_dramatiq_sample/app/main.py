import random

import app.settings as settings
from app.tasks import add_delayed, add_high, add_low, always_fails
from fastapi import FastAPI
from fastapi.logger import logger
from fastapi.responses import HTMLResponse, RedirectResponse

from judoscale.asgi.middleware import FastAPIRequestQueueTimeMiddleware


def publish_task(i=1):
    if random.random() > 0.5:
        logger.debug("Enqueuing a task on queue='high'")
        add_high.send(i, i)
    else:
        logger.debug("Enqueuing a task on queue='low'")
        add_low.send(i, i)


def create_app():
    app = FastAPI()
    app.add_middleware(
        FastAPIRequestQueueTimeMiddleware, extra_config=settings.JUDOSCALE
    )

    @app.get("/")
    async def index():
        logger.warning("Hello, world")
        if url := settings.JUDOSCALE.get("API_BASE_URL"):
            return HTMLResponse(
                "Judoscale FastAPI Dramatiq Sample App. "
                f"<a target='_blank' href={url}>Metrics</a>"
                "<form action='/task' method='POST'>"
                "<input type='submit' value='Add task'>"
                "</form>"
                "<form action='/batch_task' method='POST'>"
                "<input type='submit' value='Add 10 tasks'>"
                "</form>"
                "<form action='/delayed_task' method='POST'>"
                "<input type='submit' value='Add delayed task (30s)'>"
                "</form>"
                "<form action='/failing_task' method='POST'>"
                "<input type='submit' value='Add failing task (goes to dead queue)'>"
                "</form>"
            )
        else:
            return HTMLResponse(
                "Judoscale FastAPI Dramatiq Sample App. No API URL provided."
            )

    @app.post("/task")
    async def task():
        publish_task()
        return RedirectResponse(url="/", status_code=303)

    @app.post("/batch_task")
    async def batch_task():
        for i in range(10):
            publish_task(i)
        return RedirectResponse(url="/", status_code=303)

    @app.post("/delayed_task")
    async def delayed_task():
        add_delayed.send_with_options(args=(1, 2), delay=30000)
        return RedirectResponse(url="/", status_code=303)

    @app.post("/failing_task")
    async def failing_task():
        always_fails.send()
        return RedirectResponse(url="/", status_code=303)

    return app
