from pydantic import BaseSettings


class JudoscaleSettings(BaseSettings):
    log_level: str = "DEBUG"
    api_base_url: str = "https://requestinspector.com/inspect/judoscale-fastapi"


class Settings(BaseSettings):
    app_name: str = "judoscale-fastapi"
    judoscale: JudoscaleSettings = JudoscaleSettings()

    class Config:
        env_nested_delimiter = "__"


settings = Settings()
