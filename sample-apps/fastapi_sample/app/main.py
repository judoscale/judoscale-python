from app.config import settings
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from judoscale.asgi.middleware import RequestQueueTimeMiddleware
from judoscale.core.config import config as judoconfig


def create_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        RequestQueueTimeMiddleware, extra_config=settings.judoscale.dict()
    )

    @app.get("/")
    async def index():
        catcher_url = judoconfig["API_BASE_URL"].replace("/inspect/", "/p/")
        return HTMLResponse(
            "Judoscale FastAPI Sample App. "
            f"<a target='_blank' href={catcher_url}>Metrics</a>"
        )

    return app
