from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls import url, patterns, include
import debug_toolbar

from mps import settings

# from .views import CustomSearch
from .views import custom_search

admin.autodiscover()

urlpatterns = patterns('',

                       url(r'^$', 'mps.views.main'),

                       # user auth urls
                       url(r'^accounts/login/$',  'mps.views.login'),
                       url(r'^accounts/auth/$',  'mps.views.auth_view'),
                       url(r'^accounts/logout/$', 'mps.views.logout'),
                       url(r'^accounts/loggedin/$', 'mps.views.loggedin'),
                       url(r'^accounts/invalid/$', 'mps.views.invalid_login'),
                       url(r'^password_change/$', 'django.contrib.auth.views.password_change',
                           {'template_name': 'password_change.html'}),
                       url(r'^password_change_done/$', 'django.contrib.auth.views.password_change_done',
                           {'template_name': 'password_change_done.html'}, name="password_change_done"),

                       # Comment out captchas for now
                       # Captchas
                       # url(r'^captcha/', include('captcha.urls')),

                       # Help
                       url(r'^help/', 'mps.views.help'),

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
                       url(r'^assays_ajax$', 'assays.ajax.ajax'),
                       url(r'^compounds_ajax$', 'compounds.ajax.ajax'),
                       url(r'^cellsamples_ajax$', 'cellsamples.ajax.ajax'),
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

