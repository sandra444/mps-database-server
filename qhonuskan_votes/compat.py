from django import VERSION as DJANGO_VERSION


if DJANGO_VERSION >= (1, 5) and DJANGO_VERSION < (1, 7):
    from django.conf.urls import *
    from django.contrib.auth import get_user_model

    User = get_user_model()

elif DJANGO_VERSION >= (1, 7):
    from django.conf import settings
    try:
        from django.contrib.auth import get_user_model
        User = settings.AUTH_USER_MODEL
    except ImportError:
        from django.contrib.auth.models import User

else:
    from django.conf.urls.defaults import *
    from django.contrib.auth.models import User
