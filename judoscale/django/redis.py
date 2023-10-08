import os

from redis import Redis


class RedisHelper:
    def redis_connection(self, redis_config: dict = None) -> Redis:
        """
        Return a Redis connection from an RQ queue configuration
        """
        if redis_config is not None:
            config = {k.lower(): v for k, v in redis_config.items()}
            if redis_url := config.get("url"):
                del config["url"]
                return Redis.from_url(redis_url, **config)
            else:
                return Redis(**config)
        elif redis_url := os.getenv("REDIS_URL"):
            return Redis.from_url(redis_url)
        else:
            raise RuntimeError(
                "Missing Redis connection configuration. Please set either "
                "settings.JUDOSCALE['REDIS'] or REDIS_URL environment variable."
            )
