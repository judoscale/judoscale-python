from pytest import fixture

from judoscale.core.config import Config


@fixture
def heroku_release_1(monkeypatch):
    monkeypatch.setenv("JUDOSCALE_URL", "https://api.example.com")
    monkeypatch.setenv("DYNO", "release.1")
    return Config.initialize()


@fixture
def heroku_web_1(monkeypatch):
    monkeypatch.setenv("JUDOSCALE_URL", "https://api.example.com")
    monkeypatch.setenv("DYNO", "web.1")
    return Config.initialize()


@fixture
def heroku_web_2(monkeypatch):
    monkeypatch.setenv("JUDOSCALE_URL", "https://api.example.com")
    monkeypatch.setenv("DYNO", "web.2")
    return Config.initialize()


@fixture
def heroku_worker_1(monkeypatch):
    monkeypatch.setenv("JUDOSCALE_URL", "https://api.example.com")
    monkeypatch.setenv("DYNO", "worker.1")
    return Config.initialize()


@fixture
def heroku_worker_2(monkeypatch):
    monkeypatch.setenv("JUDOSCALE_URL", "https://api.example.com")
    monkeypatch.setenv("DYNO", "worker.2")
    return Config.initialize()


@fixture
def render_web(monkeypatch):
    monkeypatch.setenv("RENDER_SERVICE_ID", "srv-cretl9aj1k6c73a9b6lg")
    monkeypatch.setenv(
        "RENDER_INSTANCE_ID", "srv-cretl9aj1k6c73a9b6lg-5c686f7df6-kb6kj"
    )
    return Config.initialize()


@fixture
def render_worker(monkeypatch):
    monkeypatch.setenv("RENDER_SERVICE_ID", "srv-cretl9aj1k6c73a9b6lg")
    monkeypatch.setenv(
        "RENDER_INSTANCE_ID", "srv-cretl9aj1k6c73a9b6lg-5c686f7df6-2dptk"
    )
    return Config.initialize()


@fixture
def scalingo_web_1(monkeypatch):
    monkeypatch.setenv("JUDOSCALE_URL", "https://api.example.com")
    monkeypatch.setenv("CONTAINER", "web-1")
    return Config.initialize()


@fixture
def scalingo_web_2(monkeypatch):
    monkeypatch.setenv("JUDOSCALE_URL", "https://api.example.com")
    monkeypatch.setenv("CONTAINER", "web-2")
    return Config.initialize()


@fixture
def scalingo_worker_1(monkeypatch):
    monkeypatch.setenv("JUDOSCALE_URL", "https://api.example.com")
    monkeypatch.setenv("CONTAINER", "worker-1")
    return Config.initialize()


@fixture
def scalingo_worker_2(monkeypatch):
    monkeypatch.setenv("JUDOSCALE_URL", "https://api.example.com")
    monkeypatch.setenv("CONTAINER", "worker-2")
    return Config.initialize()


@fixture(
    params=[
        "heroku_web_1",
        "heroku_web_2",
        "render_web",
        "scalingo_web_1",
        "scalingo_web_2",
    ]
)
def web_all(request):
    return request.getfixturevalue(request.param)


@fixture(params=["heroku_web_1", "render_web", "scalingo_web_1"])
def web_1(request):
    return request.getfixturevalue(request.param)


@fixture(
    params=[
        "heroku_worker_1",
        "heroku_worker_2",
        "render_worker",
        "scalingo_worker_1",
        "scalingo_worker_2",
    ]
)
def worker_all(request):
    return request.getfixturevalue(request.param)


@fixture(params=["heroku_worker_1", "render_worker", "scalingo_worker_1"])
def worker_1(request):
    return request.getfixturevalue(request.param)
