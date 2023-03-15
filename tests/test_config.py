from judoscale.core.config import Config, RuntimeContainer


class TestConfig:
    def test_on_heroku(self):
        fake_env = {
            "DYNO": "web.1",
            "LOG_LEVEL": "WARN",
            "JUDOSCALE_URL": "https://api.example.com",
        }
        config = Config.for_heroku(fake_env)

        assert config.runtime_container.service_name == "web"
        assert config.runtime_container.instance == "1"
        assert config.runtime_container.service_type == "web"
        assert config.log_level == "WARN"
        assert config.api_base_url == "https://api.example.com"

    def test_on_render(self):
        fake_env = {
            "RENDER_SERVICE_ID": "srv-123",
            "RENDER_INSTANCE_ID": "srv-123-abc-456",
            "RENDER_SERVICE_TYPE": "web",
            "LOG_LEVEL": "WARN",
        }
        config = Config.for_render(fake_env)

        assert config.runtime_container.service_name == "srv-123"
        assert config.runtime_container.instance == "abc-456"
        assert config.runtime_container.service_type == "web"
        assert config.log_level == "WARN"
        assert config.api_base_url == "https://adapter.judoscale.com/api/srv-123"


class TestRuntimeContainer:
    def test_is_web_instance(self):
        container = RuntimeContainer("web", "1", "web")
        assert container.is_web_instance

    def test_is_not_web_instance(self):
        container = RuntimeContainer("worker", "1", "other")
        assert not container.is_web_instance

    def test_is_redundant_instance(self):
        container = RuntimeContainer("web", "2", "web")
        assert container.is_redundant_instance

    def test_is_not_redundant_instance(self):
        container = RuntimeContainer("web", "1", "web")
        assert not container.is_redundant_instance

    def test_string_representation(self):
        container = RuntimeContainer("web", "1", "web")
        assert str(container) == "web.1"
