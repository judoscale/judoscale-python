from app.config import settings
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from judoscale.asgi.middleware import FastAPIRequestQueueTimeMiddleware
from judoscale.core.config import config as judoconfig


def create_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        FastAPIRequestQueueTimeMiddleware,
        extra_config=settings.judoscale.dict(),
    )

    @app.get("/")
    async def index():
        if url := judoconfig.get("API_BASE_URL"):
            catcher_url = url.replace("/inspect/", "/p/")
            return HTMLResponse(
                "Judoscale FastAPI Sample App. "
                f"<a target='_blank' href={catcher_url}>Metrics</a>"
            )
        else:
            return HTMLResponse("Judoscale FastAPI Sample App. No API URL provided.")

    return app
