import pytest

from judoscale.core.config import Config
from judoscale.core.platform import (
    Custom,
    Ecs,
    Fly,
    Heroku,
    Platform,
    Railway,
    Render,
    Scalingo,
    Unknown,
)
from judoscale.django.redis import RedisHelper


class TestConfig:
    def test_on_heroku(self):
        fake_env = {
            "DYNO": "web.1",
            "LOG_LEVEL": "WARN",
            "JUDOSCALE_URL": "https://adapter.judoscale.com/api/1234567890",
        }
        config = Config.initialize(fake_env)

        assert config["PLATFORM"].container == "web.1"
        assert config["LOG_LEVEL"] == "WARN"
        assert config["API_BASE_URL"] == "https://adapter.judoscale.com/api/1234567890"

    def test_on_render(self):
        fake_env = {
            "RENDER_SERVICE_ID": "srv-cretl9aj1k6c73a9b6lg",
            "RENDER_INSTANCE_ID": "srv-cretl9aj1k6c73a9b6lg-5c686f7df6-kb6kj",
            "RENDER_SERVICE_TYPE": "web",
            "JUDOSCALE_URL": "https://adapter.judoscale.com/api/1234567890",
            "LOG_LEVEL": "WARN",
        }
        config = Config.initialize(fake_env)

        assert config["PLATFORM"].container == "5c686f7df6-kb6kj"
        assert config["LOG_LEVEL"] == "WARN"
        assert config["API_BASE_URL"] == "https://adapter.judoscale.com/api/1234567890"

    def test_on_render_legacy(self):
        fake_env = {
            "RENDER_SERVICE_ID": "srv-cretl9aj1k6c73a9b6lg",
            "RENDER_INSTANCE_ID": "srv-cretl9aj1k6c73a9b6lg-5c686f7df6-kb6kj",
            "RENDER_SERVICE_TYPE": "web",
            "LOG_LEVEL": "WARN",
        }
        config = Config.initialize(fake_env)

        assert config["PLATFORM"].container == "5c686f7df6-kb6kj"
        assert config["LOG_LEVEL"] == "WARN"
        assert (
            config["API_BASE_URL"]
            == "https://adapter.judoscale.com/api/srv-cretl9aj1k6c73a9b6lg"
        )
        assert config.is_enabled

    def test_on_ecs(self):
        fake_env = {
            "ECS_CONTAINER_METADATA_URI": "http://169.254.170.2/v3/a8880ee042bc4db3ba878dce65b769b6-2750272591",  # noqa
            "JUDOSCALE_URL": "https://adapter.judoscale.com/api/1234567890",
            "LOG_LEVEL": "WARN",
        }
        config = Config.initialize(fake_env)

        assert (
            config["PLATFORM"].container
            == "a8880ee042bc4db3ba878dce65b769b6-2750272591"
        )
        assert config["LOG_LEVEL"] == "WARN"
        assert config["API_BASE_URL"] == "https://adapter.judoscale.com/api/1234567890"

    def test_on_fly(self):
        fake_env = {
            "FLY_MACHINE_ID": "683d924b322418",
            "FLY_PROCESS_GROUP": "web",
            "JUDOSCALE_URL": "https://adapter.judoscale.com/api/1234567890",
            "LOG_LEVEL": "WARN",
        }
        config = Config.initialize(fake_env)

        assert config["PLATFORM"].container == "683d924b322418"
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

        assert config["PLATFORM"].container == "f9c88b6e-0e96-46f2-9884-ece3bf53d009"
        assert config["LOG_LEVEL"] == "WARN"
        assert config["API_BASE_URL"] == "https://adapter.judoscale.com/api/1234567890"

    def test_on_scalingo(self):
        fake_env = {
            "CONTAINER": "web-1",
            "JUDOSCALE_URL": "https://adapter.judoscale.com/api/1234567890",
            "LOG_LEVEL": "WARN",
        }
        config = Config.initialize(fake_env)

        assert config["PLATFORM"].container == "web-1"
        assert config["LOG_LEVEL"] == "WARN"
        assert config["API_BASE_URL"] == "https://adapter.judoscale.com/api/1234567890"

    def test_on_custom(self):
        fake_env = {
            "JUDOSCALE_CONTAINER": "my-custom-container",
            "JUDOSCALE_URL": "https://adapter.judoscale.com/api/1234567890",
        }
        config = Config.initialize(fake_env)

        assert config["PLATFORM"].container == "my-custom-container"
        assert config["LOG_LEVEL"] == "WARN"
        assert config["API_BASE_URL"] == "https://adapter.judoscale.com/api/1234567890"

    def test_on_custom_takes_precedence(self):
        fake_env = {
            "JUDOSCALE_CONTAINER": "my-custom-container",
            "DYNO": "web.1",
            "JUDOSCALE_URL": "https://adapter.judoscale.com/api/1234567890",
        }
        config = Config.initialize(fake_env)

        assert config["PLATFORM"].container == "my-custom-container"

    def test_on_unknown(self):
        fake_env = {"JUDOSCALE_URL": "https://adapter.judoscale.com/api/1234567890"}
        config = Config.initialize(fake_env)

        assert config["PLATFORM"].container == ""
        assert config["LOG_LEVEL"] == "WARN"
        assert config["API_BASE_URL"] == "https://adapter.judoscale.com/api/1234567890"

    def test_judoscale_log_level_env(self):
        fake_env = {
            "DYNO": "web.1",
            "LOG_LEVEL": "INFO",
            "JUDOSCALE_LOG_LEVEL": "WARN",
            "JUDOSCALE_URL": "https://api.example.com",
        }
        config = Config.initialize(fake_env)

        assert config["PLATFORM"].container == "web.1"
        assert config["LOG_LEVEL"] == "WARN"
        assert config["API_BASE_URL"] == "https://api.example.com"

    def test_is_enabled(self):
        config = Config(Unknown(""), {})
        assert not config.is_enabled

        config = Config(Unknown(""), {"JUDOSCALE_URL": "https://some-url.com"})
        assert config.is_enabled

    def test_for_report(self):
        fake_env = {
            "DYNO": "web.1",
            "LOG_LEVEL": "WARN",
            "JUDOSCALE_URL": "https://api.example.com",
        }
        config = Config.initialize(fake_env)
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
        config = Config.initialize(fake_env)
        assert config["API_BASE_URL"] == "https://api.example.com"
        assert config["PLATFORM"].container == "worker.1"
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
        config = Config.initialize(fake_env)
        assert config["LOG_LEVEL"] == "WARN"
        assert config["REPORT_INTERVAL_SECONDS"] == 10

        config.update({"log_level": "error", "report_interval_seconds": 20})
        assert config["LOG_LEVEL"] == "error"
        assert config["REPORT_INTERVAL_SECONDS"] == 20


class TestPlatform:
    def test_detects_the_platform_from_env_with_custom_winning(self):
        # An explicit JUDOSCALE_CONTAINER always wins over platform vars.
        assert isinstance(
            Platform.detect({"JUDOSCALE_CONTAINER": "x", "DYNO": "web.1"}), Custom
        )
        assert isinstance(Platform.detect({"DYNO": "web.1"}), Heroku)
        assert isinstance(
            Platform.detect(
                {"RENDER_INSTANCE_ID": "srv-x-abc", "RENDER_SERVICE_ID": "srv-x"}
            ),
            Render,
        )
        assert isinstance(
            Platform.detect(
                {"ECS_CONTAINER_METADATA_URI": "http://169.254.170.2/v3/abc"}
            ),
            Ecs,
        )
        assert isinstance(Platform.detect({"FLY_MACHINE_ID": "683d924b322418"}), Fly)
        assert isinstance(Platform.detect({"RAILWAY_REPLICA_ID": "f9c88b6e"}), Railway)
        assert isinstance(Platform.detect({"CONTAINER": "web-1"}), Scalingo)
        assert isinstance(Platform.detect({}), Unknown)

    def test_treats_only_ordinals_beyond_the_first_as_redundant(self):
        assert not Heroku("web.1").is_redundant_instance
        assert not Heroku("custom_name.1").is_redundant_instance
        assert Heroku("web.2").is_redundant_instance
        assert Heroku("custom_name.15").is_redundant_instance
        assert not Scalingo("web-1").is_redundant_instance
        assert not Scalingo("tcp-1").is_redundant_instance
        assert Scalingo("web-2").is_redundant_instance
        assert Scalingo("tcp-2").is_redundant_instance
        # No 3-digit cap — formations with 1000+ instances are still redundant.
        assert Heroku("web.1000").is_redundant_instance
        assert Scalingo("worker-1024").is_redundant_instance

    def test_never_treats_opaque_id_platforms_as_redundant(self):
        assert not Render("5497f74465-m5wwr", service_id="srv-x").is_redundant_instance
        # Realistic Render container id with a digit-leading suffix.
        assert not Render(
            "srv-x-5c686f7df6-2dptk", service_id="srv-x"
        ).is_redundant_instance
        assert not Ecs(
            "a8880ee042bc4db3ba878dce65b769b6-2750272591"
        ).is_redundant_instance
        assert not Fly("683d924b322418").is_redundant_instance
        assert not Railway("f9c88b6e-0e96-46f2-9884-ece3bf53d009").is_redundant_instance
        assert not Custom("abcdef-2750272591").is_redundant_instance
        assert not Unknown("").is_redundant_instance

    def test_treats_heroku_release_phase_and_one_off_dynos_as_ephemeral(self):
        assert Heroku("release.1").is_ephemeral_instance
        assert Heroku("run.1234").is_ephemeral_instance

    def test_treats_scalingo_one_off_containers_as_ephemeral(self):
        assert Scalingo("one-off-1234").is_ephemeral_instance

    def test_does_not_treat_formation_containers_as_ephemeral(self):
        assert not Heroku("web.1").is_ephemeral_instance
        assert not Heroku("worker.2").is_ephemeral_instance
        assert not Heroku("runner-1").is_ephemeral_instance
        assert not Scalingo("web-1").is_ephemeral_instance
        assert not Scalingo("worker-2").is_ephemeral_instance

    def test_never_treats_opaque_id_platforms_as_ephemeral(self):
        assert not Render("5497f74465-m5wwr", service_id="srv-x").is_ephemeral_instance
        assert not Fly("683d924b322418").is_ephemeral_instance
        assert not Unknown("").is_ephemeral_instance

    def test_strips_the_service_id_prefix_from_the_render_instance_id(self):
        assert (
            Render("srv-x-5497f74465-m5wwr", service_id="srv-x").container
            == "5497f74465-m5wwr"
        )

    def test_lets_legacy_render_services_derive_the_api_url_from_the_service_id(self):
        assert (
            Render("abc", service_id="srv-x").default_api_base_url
            == "https://adapter.judoscale.com/api/srv-x"
        )
        assert Heroku("web.1").default_api_base_url is None

    def test_container_is_stringified(self):
        assert Heroku("web.1").container == "web.1"


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
