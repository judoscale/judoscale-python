import dramatiq
from django.conf import settings

from judoscale.dramatiq import judoscale_dramatiq

broker = dramatiq.get_broker()
judoscale_dramatiq(broker, extra_config=settings.JUDOSCALE)
