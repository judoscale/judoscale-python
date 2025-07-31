import time, random
import settings
from flask import Flask, current_app, request

from judoscale.core.utilization_tracker import utilization_tracker
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

    @app.route("/test_utilization_tracker", methods=["GET"])
    def test_utilization_tracker():
        # Run utilization tracker in the foreground to execute the tracking mid-request.
        utilization_tracker._track_current_state()

        return f"utilization_tracker={utilization_tracker.active_requests}"

    return app


if __name__ == "__main__":
    create_app().run("127.0.0.1", "5000", debug=True)
