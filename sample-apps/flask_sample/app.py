import settings
from flask import Flask, current_app

from judoscale.flask import Judoscale

judoscale = Judoscale()


def create_app():
    app = Flask("DemoFlaskApp")
    app.config.from_object(settings.BaseConfig)

    judoscale.init_app(app)

    @app.route("/", methods=["GET"])
    def index():
        current_app.logger.warning("Hello, world")
        catcher_url = current_app.config["JUDOSCALE"]["API_BASE_URL"].replace(
            "/inspect/", "/p/"
        )
        return (
            "Judoscale Flask Sample App. "
            f"<a target='_blank' href={catcher_url}>Metrics</a>"
        )

    return app


if __name__ == "__main__":
    create_app().run("127.0.0.1", "5000", debug=True)
