import random

import app.settings as settings
from app.tasks import add
from fastapi import FastAPI
from fastapi.logger import logger
from fastapi.responses import HTMLResponse, RedirectResponse

from judoscale.asgi.middleware import RequestQueueTimeMiddleware


def publish_task(i=1):
    queue = "high" if random.random() > 0.5 else "low"
    logger.debug(f"Enqueuing a task on {queue=}")
    add.s(i, i).apply_async(queue=queue)


def create_app():
    app = FastAPI()
    app.add_middleware(RequestQueueTimeMiddleware, extra_config=settings.JUDOSCALE)

    @app.get("/")
    async def index():
        logger.warning("Hello, world")
        catcher_url = settings.JUDOSCALE["API_BASE_URL"].replace("/inspect/", "/p/")
        return HTMLResponse(
            "Judoscale FastAPI Celery Sample App. "
            f"<a target='_blank' href={catcher_url}>Metrics</a>"
            "<form action='/task' method='POST'>"
            "<input type='submit' value='Add task'>"
            "</form>"
            "<form action='/batch_task' method='POST'>"
            "<input type='submit' value='Add 10 tasks'>"
            "</form>"
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

    return app
