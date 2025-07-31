import time, random
import app.settings as settings
from fastapi import FastAPI
from fastapi.logger import logger
from fastapi.responses import HTMLResponse

from judoscale.asgi.middleware import FastAPIRequestQueueTimeMiddleware
from judoscale.core.config import config as judoconfig
from judoscale.core.utilization_tracker import utilization_tracker


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
            time.sleep(random.randint(0,2))

        if url := judoconfig.get("API_BASE_URL"):
            return HTMLResponse(
                "Judoscale FastAPI Sample App. "
                f"<a target='_blank' href={url}>Metrics</a>"
            )
        else:
            return HTMLResponse("Judoscale FastAPI Sample App. No API URL provided.")

    @app.get("/test_utilization_tracker")
    async def test_utilization_tracker():
        # Run utilization tracker in the foreground to execute the tracking mid-request.
        utilization_tracker._track_current_state()

        return HTMLResponse(f"utilization_tracker={utilization_tracker.active_requests}")

    return app
