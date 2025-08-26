import time, random
import app.settings as settings
from fastapi import FastAPI
from fastapi.logger import logger
from fastapi.responses import HTMLResponse

from judoscale.asgi.middleware import FastAPIRequestQueueTimeMiddleware
from judoscale.core.config import config as judoconfig


def create_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        FastAPIRequestQueueTimeMiddleware,
        extra_config=settings.JUDOSCALE,
    )

    @app.get("/")
    async def index(sleep = None):
        logger.warning("Hello, world")

        if sleep:
            try:
                sleep_for = float(sleep)
            except:
                sleep_for = random.randint(0, 2)
            time.sleep(sleep_for)

        if url := judoconfig.get("API_BASE_URL"):
            return HTMLResponse(
                "Judoscale FastAPI Sample App. "
                f"<a target='_blank' href={url}>Metrics</a>"
            )
        else:
            return HTMLResponse("Judoscale FastAPI Sample App. No API URL provided.")

    return app
