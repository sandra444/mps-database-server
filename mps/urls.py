from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls import url, patterns, include
import debug_toolbar

from mps import settings

# from .views import CustomSearch
from .views import custom_search

# For registration
from django.views.generic.base import TemplateView
from registration.backends.hmac.views import ActivationView, RegistrationView
from django.contrib.auth import views as auth_views

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', 'mps.views.main'),

    # user auth urls
    url(r'^accounts/login/$',  'mps.views.login', name='auth_login'),
    url(r'^accounts/auth/$',  'mps.views.auth_view', name='auth'),
    url(r'^accounts/logout/$', 'mps.views.logout', name='auth_logout'),
    url(r'^accounts/loggedin/$', 'mps.views.loggedin', name='auth_loggedin'),
    url(
        r'^accounts/invalid/$',
        'mps.views.invalid_login',
        name='auth_invalid'
    ),
    url(
        r'^password_change/$',
        'django.contrib.auth.views.password_change',
        {'template_name': 'password_change.html'},
        name='password_change'
    ),
    url(
        r'^password_change_done/$',
        'django.contrib.auth.views.password_change_done',
        {'template_name': 'password_change_done.html'},
        name="password_change_done"
    ),

    # Registration
    url(
        r'^activate/complete/$',
        TemplateView.as_view(
            template_name='registration/activation_complete.html'
        ),
        name='registration_activation_complete'
    ),
    # The activation key can make use of any character from the
    # URL-safe base64 alphabet, plus the colon as a separator.
    url(
        r'^activate/(?P<activation_key>[-:\w]+)/$',
        ActivationView.as_view(),
        name='registration_activate'
    ),
    url(
        r'^register/$',
        RegistrationView.as_view(),
        name='registration_register'
    ),
    url(
        r'^register/complete/$',
        TemplateView.as_view(
            template_name='registration/registration_complete.html'
        ),
        name='registration_complete'
    ),
    url(
        r'^register/closed/$',
        TemplateView.as_view(
            template_name='registration/registration_closed.html'
        ),
        name='registration_disallowed'
    ),

    # Password Reset
    url(
        r'^password/reset/$',
        auth_views.password_reset,
        {'post_reset_redirect': 'auth_password_reset_done',
         'email_template_name': 'registration/password_reset_email.txt'},
        name='auth_password_reset'
    ),
    url(
        r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/'
        r'(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm,
        {'post_reset_redirect': 'auth_password_reset_complete'},
        name='auth_password_reset_confirm'
    ),
    url(
        r'^password/reset/complete/$',
        auth_views.password_reset_complete,
        name='auth_password_reset_complete'
    ),
    url(
        r'^password/reset/done/$',
        auth_views.password_reset_done,
        name='auth_password_reset_done'
    ),

    # Comment out captchas for now
    # Captchas
    # url(r'^captcha/', include('captcha.urls')),

    # Help
    url(r'^help/', 'mps.views.mps_help'),

    # Djangovoice for feedback
    url(r'^comments/', include('django_comments.urls')),
    url(r'^feedback/', include('djangovoice.urls')),

    # The frontend
    url(r'^', include('bioactivities.urls')),
    url(r'^', include('assays.urls')),
    url(r'^', include('compounds.urls')),
    url(r'^', include('microdevices.urls')),
    url(r'^', include('drugtrials.urls')),
    url(r'^', include('cellsamples.urls')),

    # Default search via haystack/whoosh
    (r'^haystack/', include('haystack.urls')),
    # Testing custom search (same as default currently)
    # (r'^search/', CustomSearch()),
    (r'^search/', custom_search),


    # BEGIN old-style API
    url(r'^search_ajax/$', 'mps.ajax.ajax'),
    url(r'^assays_ajax/$', 'assays.ajax.ajax'),
    url(r'^compounds_ajax/$', 'compounds.ajax.ajax'),
    url(r'^cellsamples_ajax/$', 'cellsamples.ajax.ajax'),
    # END old-style API

    url(
        r'^admin/doc/',
        include('django.contrib.admindocs.urls')
    ),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^webhook$', 'mps.management.webhook'),
    url(r'^database$', 'mps.management.database'),

    url(
        r'^media/(?P<path>.*)$',
        'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}
    ),
    url(r'^__debug__/', include(debug_toolbar.urls)),
)

# Note that the URL path can be whatever you want, but you must include
# rest_framework.urls' with the 'rest_framework' namespace.

urlpatterns += staticfiles_urlpatterns()
