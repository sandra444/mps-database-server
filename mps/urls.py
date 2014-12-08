from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls import url, patterns, include
import debug_toolbar

from mps import settings


admin.autodiscover()

urlpatterns = patterns('',

                       url(r'^$', 'mps.views.main'),

                       # user auth urls
                       url(r'^accounts/login/$',  'mps.views.login'),
                       url(r'^accounts/auth/$',  'mps.views.auth_view'),
                       url(r'^accounts/logout/$', 'mps.views.logout'),
                       url(r'^accounts/loggedin/$', 'mps.views.loggedin'),
                       url(r'^accounts/invalid/$', 'mps.views.invalid_login'),
                       # url(r'^accounts/register/$', 'mps.views.register_user'),
                       # url(r'^accounts/register_success/$', 'mps.views.register_success'),

                       # Captchas
                       url(r'^captcha/', include('captcha.urls')),

                       # The frontend
                       url(r'^', include('bioactivities.urls')),
                       url(r'^', include('assays.urls')),
                       url(r'^', include('compounds.urls')),

                       # BEGIN old-style API
                       url(r'^assays_ajax$', 'assays.ajax.ajax'),
                       url(r'^compounds_ajax$', 'compounds.ajax.ajax'),
                       # END old-style API

                       url(r'^admin/doc/',
                           include('django.contrib.admindocs.urls')),
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

