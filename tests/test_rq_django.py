from types import SimpleNamespace
from unittest.mock import patch

import judoscale.rq as rq_module
from judoscale.rq.apps import JudoscaleRQConfig


class TestJudoscaleRQConfig:
    def test_ready_without_judoscale_setting_falls_back_to_redis_url(self, monkeypatch):
        monkeypatch.setenv("REDIS_URL", "redis://localhost:1234/5")

        config = JudoscaleRQConfig("judoscale.rq", rq_module)

        with (
            patch("judoscale.rq.apps.settings", SimpleNamespace()),
            patch("judoscale.rq.apps.judoconfig") as judoconfig,
            patch("judoscale.rq.apps.judoscale_rq") as mock_judoscale_rq,
            patch("judoscale.rq.apps.reporter"),
        ):
            judoconfig.is_enabled = True
            config.ready()

        judoconfig.update.assert_called_once_with({})
        redis = mock_judoscale_rq.call_args[0][0]
        assert redis.connection_pool.connection_kwargs == {
            "host": "localhost",
            "port": 1234,
            "db": 5,
        }

    def test_ready_with_judoscale_redis_config(self):
        settings = SimpleNamespace(
            JUDOSCALE={"REDIS": {"URL": "redis://localhost:6379/0"}}
        )
        config = JudoscaleRQConfig("judoscale.rq", rq_module)

        with (
            patch("judoscale.rq.apps.settings", settings),
            patch("judoscale.rq.apps.judoconfig") as judoconfig,
            patch("judoscale.rq.apps.judoscale_rq") as mock_judoscale_rq,
            patch("judoscale.rq.apps.reporter"),
        ):
            judoconfig.is_enabled = True
            config.ready()

        judoconfig.update.assert_called_once_with(settings.JUDOSCALE)
        redis = mock_judoscale_rq.call_args[0][0]
        assert redis.connection_pool.connection_kwargs == {
            "host": "localhost",
            "port": 6379,
            "db": 0,
        }
