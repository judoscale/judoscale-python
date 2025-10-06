import random

import app.settings as settings
from app.tasks import add
from fastapi import FastAPI
from fastapi.logger import logger
from fastapi.responses import HTMLResponse, RedirectResponse

from judoscale.asgi.middleware import FastAPIRequestQueueTimeMiddleware


def publish_task(i=1, countdown=None):
    queue = "high" if random.random() > 0.5 else "low"
    logger.debug(f"Enqueuing a task on {queue=}")
    add.s(i, i).apply_async(queue=queue, countdown=countdown)


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
                "Judoscale FastAPI Celery Sample App. "
                f"<a target='_blank' href={url}>Metrics</a>"
                "<form action='/task' method='POST'>"
                "<input type='submit' value='Add task'>"
                "</form>"
                "<form action='/batch_task' method='POST'>"
                "<input type='submit' value='Add 10 tasks'>"
                "</form>"
                "<form action='/schedule_task' method='POST'>"
                "<input type='submit' value='Add scheduled task'>"
                "</form>"
                "<form action='/batch_schedule_task' method='POST'>"
                "<input type='submit' value='Add 10 scheduled tasks'>"
                "</form>"
            )
        else:
            return HTMLResponse(
                "Judoscale FastAPI Celery Sample App. No API URL provided."
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

    @app.post("/schedule_task")
    async def schedule_task():
        publish_task(countdown=120)
        return RedirectResponse(url="/", status_code=303)

    @app.post("/batch_schedule_task")
    async def batch_schedule_task():
        for i in range(10):
            publish_task(i, countdown=120)
        return RedirectResponse(url="/", status_code=303)

    return app
