import logging
from judoscale.core.config import config as judoconfig
from judoscale.flask.middleware import RequestQueueTimeMiddleware

from flask import Flask, request
import settings

logger = logging.getLogger(__name__)


app = Flask("DemoFlaskApp")
config_obj = settings.BaseConfig
app.config.from_object(config_obj)

judoconfig.merge(getattr(config_obj, "JUDOSCALE", {}))

# calling our middleware
app.wsgi_app = RequestQueueTimeMiddleware(app.wsgi_app)


@app.route("/", methods=["GET"])
def index():
    logger.debug("Hello World")
    print("Hello World")
    return f"Welcome to Judoscale {request.environ}"


if __name__ == "__main__":
    app.run("127.0.0.1", "5000", debug=True)
