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
        return "Judoscale Flask Sample App"

    return app


if __name__ == "__main__":
    create_app().run("127.0.0.1", "5000", debug=True)
