import time, random
import settings
from flask import Flask, current_app, request

from judoscale.flask import Judoscale

judoscale = Judoscale()


def create_app():
    app = Flask("DemoFlaskApp")
    app.config.from_object(settings.BaseConfig)

    judoscale.init_app(app)

    @app.route("/", methods=["GET"])
    def index():
        current_app.logger.warning("Hello, world")

        if request.args.get("sleep"):
            time.sleep(random.randint(0,2))

        if url := current_app.config["JUDOSCALE"].get("API_BASE_URL"):
            return (
                "Judoscale Flask Sample App. "
                f"<a target='_blank' href={url}>Metrics</a>"
            )
        else:
            return "Judoscale Flask Sample App. No API URL provided."

    return app


if __name__ == "__main__":
    create_app().run("127.0.0.1", "5000", debug=True)
