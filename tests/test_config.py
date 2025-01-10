import pytest

from judoscale.core.config import Config, RuntimeContainer
from judoscale.django.redis import RedisHelper


class TestConfig:
    def test_on_heroku(self):
        fake_env = {
            "DYNO": "web.1",
            "LOG_LEVEL": "WARN",
            "JUDOSCALE_URL": "https://adapter.judoscale.com/api/1234567890",
        }
        config = Config.initialize(fake_env)

        assert config["RUNTIME_CONTAINER"] == "web.1"
        assert config["LOG_LEVEL"] == "WARN"
        assert config["API_BASE_URL"] == "https://adapter.judoscale.com/api/1234567890"

    def test_on_render(self):
        fake_env = {
            "RENDER_SERVICE_ID": "srv-123",
            "RENDER_INSTANCE_ID": "srv-123-abc-456",
            "RENDER_SERVICE_TYPE": "web",
            "JUDOSCALE_URL": "https://adapter.judoscale.com/api/1234567890",
            "LOG_LEVEL": "WARN",
        }
        config = Config.initialize(fake_env)

        assert config["RUNTIME_CONTAINER"] == "abc-456"
        assert config["LOG_LEVEL"] == "WARN"
        assert config["API_BASE_URL"] == "https://adapter.judoscale.com/api/1234567890"

    def test_on_render_legacy(self):
        fake_env = {
            "RENDER_SERVICE_ID": "srv-123",
            "RENDER_INSTANCE_ID": "srv-123-abc-456",
            "RENDER_SERVICE_TYPE": "web",
            "LOG_LEVEL": "WARN",
        }
        config = Config.initialize(fake_env)

        assert config["RUNTIME_CONTAINER"] == "abc-456"
        assert config["LOG_LEVEL"] == "WARN"
        assert config["API_BASE_URL"] == "https://adapter.judoscale.com/api/srv-123"

    def test_on_ecs(self):
        fake_env = {
            "ECS_CONTAINER_METADATA_URI": "http://169.254.170.2/v3/a8880ee042bc4db3ba878dce65b769b6-2750272591",  # noqa
            "JUDOSCALE_URL": "https://adapter.judoscale.com/api/1234567890",
            "LOG_LEVEL": "WARN",
        }
        config = Config.initialize(fake_env)

        assert (
            config["RUNTIME_CONTAINER"] == "a8880ee042bc4db3ba878dce65b769b6-2750272591"
        )
        assert config["LOG_LEVEL"] == "WARN"
        assert config["API_BASE_URL"] == "https://adapter.judoscale.com/api/1234567890"

    def test_on_railway(self):
        fake_env = {
            "RAILWAY_SERVICE_ID": "1431de82-74ad-4f1a-b8f2-1952262d66cf",
            "RAILWAY_REPLICA_ID": "f9c88b6e-0e96-46f2-9884-ece3bf53d009",
            "JUDOSCALE_URL": "https://adapter.judoscale.com/api/1234567890",
            "LOG_LEVEL": "WARN",
        }
        config = Config.initialize(fake_env)

        assert (
            config["RUNTIME_CONTAINER"] == "f9c88b6e-0e96-46f2-9884-ece3bf53d009"
        )
        assert config["LOG_LEVEL"] == "WARN"
        assert config["API_BASE_URL"] == "https://adapter.judoscale.com/api/1234567890"

    def test_judoscale_log_level_env(self):
        fake_env = {
            "DYNO": "web.1",
            "LOG_LEVEL": "INFO",
            "JUDOSCALE_LOG_LEVEL": "WARN",
            "JUDOSCALE_URL": "https://api.example.com",
        }
        config = Config.for_heroku(fake_env)

        assert config["RUNTIME_CONTAINER"] == "web.1"
        assert config["LOG_LEVEL"] == "WARN"
        assert config["API_BASE_URL"] == "https://api.example.com"

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

    def test_is_release_instance(self):
        container = RuntimeContainer("release.1")
        assert container.is_release_instance

    def test_is_release_instance_2(self):
        container = RuntimeContainer("release.2")
        assert container.is_release_instance

    def test_is_not_redundant_instance(self):
        container = RuntimeContainer("web.1")
        assert not container.is_redundant_instance

    def test_string_representation(self):
        container = RuntimeContainer("web.1")
        assert str(container) == "web.1"


class TestRedisHelper:
    def test_without_redis_url_and_judoscale_redis_config(self):
        rh = RedisHelper()
        with pytest.raises(RuntimeError):
            rh.redis_connection(None)

    def test_with_redis_url(self):
        rh = RedisHelper()
        redis = rh.redis_connection({"URL": "redis://localhost:6379/0"})
        assert redis.connection_pool.connection_kwargs == {
            "host": "localhost",
            "port": 6379,
            "db": 0,
        }

    def test_with_rediss_url(self):
        rh = RedisHelper()
        redis = rh.redis_connection({"URL": "rediss://localhost:6379/0"})
        assert redis.connection_pool.connection_kwargs == {
            "host": "localhost",
            "port": 6379,
            "db": 0,
        }

    def test_with_rediss_config_on_heroku(self):
        rh = RedisHelper()
        redis = rh.redis_connection(
            {"URL": "rediss://localhost:6379/0", "SSL_CERT_REQS": None}
        )
        assert redis.connection_pool.connection_kwargs == {
            "ssl_cert_reqs": None,
            "host": "localhost",
            "port": 6379,
            "db": 0,
        }

    def test_with_env_var_redis_url(self, monkeypatch):
        monkeypatch.setenv("REDIS_URL", "redis://localhost:1234/5")
        rh = RedisHelper()
        redis = rh.redis_connection(None)
        assert redis.connection_pool.connection_kwargs == {
            "host": "localhost",
            "port": 1234,
            "db": 5,
        }
