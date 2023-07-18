from pytest import fixture

from judoscale.core.config import Config


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
    monkeypatch.setenv("RENDER_SERVICE_ID", "srv-123")
    monkeypatch.setenv("RENDER_INSTANCE_ID", "srv-123-abc-def")
    return Config.initialize()


@fixture
def render_worker(monkeypatch):
    monkeypatch.setenv("RENDER_SERVICE_ID", "srv-123")
    monkeypatch.setenv("RENDER_INSTANCE_ID", "srv-123-abc-def")
    return Config.initialize()


@fixture(params=["heroku_web_1", "heroku_web_2", "render_web"])
def web_all(request):
    return request.getfixturevalue(request.param)


@fixture(params=["heroku_web_1", "render_web"])
def web_1(request):
    return request.getfixturevalue(request.param)


@fixture(params=["heroku_worker_1", "heroku_worker_2", "render_worker"])
def worker_all(request):
    return request.getfixturevalue(request.param)


@fixture(params=["heroku_worker_1", "render_worker"])
def worker_1(request):
    return request.getfixturevalue(request.param)
