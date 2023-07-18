from judoscale.core.config import Config, RuntimeContainer


class TestConfig:
    def test_on_heroku(self):
        fake_env = {
            "DYNO": "web.1",
            "LOG_LEVEL": "WARN",
            "JUDOSCALE_URL": "https://api.example.com",
        }
        config = Config.for_heroku(fake_env)

        assert config["RUNTIME_CONTAINER"] == "web.1"
        assert config["LOG_LEVEL"] == "WARN"
        assert config["API_BASE_URL"] == "https://api.example.com"

    def test_on_render(self):
        fake_env = {
            "RENDER_SERVICE_ID": "srv-123",
            "RENDER_INSTANCE_ID": "srv-123-abc-456",
            "RENDER_SERVICE_TYPE": "web",
            "LOG_LEVEL": "WARN",
        }
        config = Config.for_render(fake_env)

        assert config["RUNTIME_CONTAINER"] == "abc-456"
        assert config["LOG_LEVEL"] == "WARN"
        assert config["API_BASE_URL"] == "https://adapter.judoscale.com/api/srv-123"

    def test_is_enabled(self):
        config = Config(None, "", {})
        assert not config.is_enabled

        config = Config(None, None, {})
        assert not config.is_enabled

        config = Config(None, "https://some-url.com", {})
        assert config.is_enabled

    def test_for_report(self):
        fake_env = {
            "DYNO": "web.1",
            "LOG_LEVEL": "WARN",
            "JUDOSCALE_URL": "https://api.example.com",
        }
        config = Config.for_heroku(fake_env)
        assert config.for_report == {"log_level": "WARN", "report_interval_seconds": 10}

        config.update({"LOG_LEVEL": "ERROR", "REPORT_INTERVAL_SECONDS": 20})
        assert config.for_report == {
            "log_level": "ERROR",
            "report_interval_seconds": 20,
        }

    def test_update(self):
        fake_env = {
            "DYNO": "worker.1",
            "LOG_LEVEL": "WARN",
            "JUDOSCALE_URL": "https://api.example.com",
            "RQ": {
                "ENABLED": True,
                "MAX_QUEUES": 20,
                "QUEUES": ["default", "high"],
            },
        }
        config = Config.for_heroku(fake_env)
        assert config["API_BASE_URL"] == "https://api.example.com"
        assert config["RUNTIME_CONTAINER"] == "worker.1"
        assert config["LOG_LEVEL"] == "WARN"
        assert config["REPORT_INTERVAL_SECONDS"] == 10

        config.update(
            {
                "LOG_LEVEL": "ERROR",
                "REPORT_INTERVAL_SECONDS": 20,
                "RQ": {"ENABLED": False, "QUEUES": ["low"]},
            }
        )

        assert config["LOG_LEVEL"] == "ERROR"
        assert config["REPORT_INTERVAL_SECONDS"] == 20
        assert not config["RQ"]["ENABLED"]
        assert config["RQ"]["MAX_QUEUES"] == 20
        assert config["RQ"]["QUEUES"] == ["low"]

    def test_update_lowercase_keys(self):
        fake_env = {
            "DYNO": "worker.1",
            "LOG_LEVEL": "WARN",
            "JUDOSCALE_URL": "https://api.example.com",
            "RQ": {
                "ENABLED": True,
                "MAX_QUEUES": 20,
                "QUEUES": ["default", "high"],
            },
        }
        config = Config.for_heroku(fake_env)
        assert config["LOG_LEVEL"] == "WARN"
        assert config["REPORT_INTERVAL_SECONDS"] == 10

        config.update({"log_level": "error", "report_interval_seconds": 20})
        assert config["LOG_LEVEL"] == "error"
        assert config["REPORT_INTERVAL_SECONDS"] == 20


class TestRuntimeContainer:
    def test_is_redundant_instance(self):
        container = RuntimeContainer("web.2")
        assert container.is_redundant_instance

    def test_is_not_redundant_instance(self):
        container = RuntimeContainer("web.1")
        assert not container.is_redundant_instance

    def test_string_representation(self):
        container = RuntimeContainer("web.1")
        assert str(container) == "web.1"
