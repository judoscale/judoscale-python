import os
import re
from typing import Mapping


class Platform:
    """The hosting platform we detected from the environment.

    The container/instance id is just one property of the platform — behavior
    that only applies to certain platforms (whether an instance is a redundant
    member of a formation or an ephemeral process) lives on the platform
    subclasses that actually have those concepts, instead of being re-derived
    from the shape of the container string.
    """

    def __init__(self, container):
        self.container = str(container)

    @property
    def is_redundant_instance(self) -> bool:
        """Most platforms expose opaque, non-ordinal instance ids (Render, ECS,
        Fly, Railway, custom), so by default no instance is redundant. Platforms
        that have a formation ordinal override this."""
        return False

    @property
    def is_ephemeral_instance(self) -> bool:
        """Most platforms do not expose release or one-off task containers.
        Platforms that have those concepts override this."""
        return False

    @property
    def default_api_base_url(self):
        """Platforms may contribute a default API base url when one isn't configured."""
        return None

    @classmethod
    def detect(cls, env: Mapping = os.environ) -> "Platform":
        """Detect the current platform from the environment. Order matters: an
        explicit JUDOSCALE_CONTAINER always wins, and Unknown is the fallback."""
        if env.get("JUDOSCALE_CONTAINER"):
            return Custom(env["JUDOSCALE_CONTAINER"])
        elif env.get("DYNO"):
            return Heroku(env["DYNO"])
        elif env.get("RENDER_INSTANCE_ID"):
            return Render(
                env["RENDER_INSTANCE_ID"], service_id=env.get("RENDER_SERVICE_ID")
            )
        elif env.get("ECS_CONTAINER_METADATA_URI"):
            return Ecs(env["ECS_CONTAINER_METADATA_URI"].split("/")[-1])
        elif env.get("FLY_MACHINE_ID"):
            return Fly(env["FLY_MACHINE_ID"])
        elif env.get("RAILWAY_REPLICA_ID"):
            return Railway(env["RAILWAY_REPLICA_ID"])
        elif env.get("CONTAINER"):
            # Scalingo exposes the container type and index (e.g. "web-1").
            return Scalingo(env["CONTAINER"])
        else:
            return Unknown("")


class Heroku(Platform):
    # Heroku dynos are named "web.2". We collect metrics from a single container
    # per process type, so any instance beyond the first is redundant — it would
    # only duplicate the metrics the first instance already reports.
    _ORDINAL = re.compile(r"[a-z_]+\.(\d+)")

    @property
    def is_redundant_instance(self) -> bool:
        match = self._ORDINAL.fullmatch(self.container)
        return int(match.group(1)) > 1 if match else False

    @property
    def is_ephemeral_instance(self) -> bool:
        # Heroku release phase and one-off dynos are named
        # "release.1234" and "run.1234".
        is_release = self.container.lower().startswith("release.")
        is_one_off = self.container.startswith("run.")
        return is_release or is_one_off


class Scalingo(Platform):
    # Scalingo containers are named "web-2", same redundancy rule as Heroku.
    _ORDINAL = re.compile(r"[a-z_]+-(\d+)")

    @property
    def is_redundant_instance(self) -> bool:
        match = self._ORDINAL.fullmatch(self.container)
        return int(match.group(1)) > 1 if match else False

    @property
    def is_ephemeral_instance(self) -> bool:
        # Scalingo one-off containers are named "one-off-1234".
        return self.container.startswith("one-off-")


class Render(Platform):
    def __init__(self, instance_id, service_id=None):
        self._service_id = service_id
        # Render prefixes the instance id with the service id, which isn't part
        # of the instance.
        if service_id:
            instance_id = instance_id.removeprefix(f"{service_id}-")
        super().__init__(instance_id)

    @property
    def default_api_base_url(self):
        # Legacy Render services not using JUDOSCALE_URL derive the adapter URL
        # from the service id.
        if self._service_id:
            return f"https://adapter.judoscale.com/api/{self._service_id}"
        return None


class Ecs(Platform):
    pass


class Fly(Platform):
    pass


class Railway(Platform):
    pass


class Custom(Platform):
    """User-provided container id via JUDOSCALE_CONTAINER."""

    pass


class Unknown(Platform):
    """Unsupported or undetected platform."""

    pass
