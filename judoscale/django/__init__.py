import django

if django.VERSION < (3, 2, 0):
    # Only define default_app_config when using a version earlier than 3.2
    # https://docs.djangoproject.com/en/4.2/releases/3.2/#what-s-new-in-django-3-2
    default_app_config = "judoscale.django.apps.JudoscaleDjangoConfig"
