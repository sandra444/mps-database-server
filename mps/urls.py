from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls import url, patterns, include
from mps import settings

admin.autodiscover()

urlpatterns = patterns('',

                       url(r'^$', 'mps.views.main'),

                       url(r'^', include('bioactivities.urls')),

                       # BEGIN old-style API
                       url(r'^assays_ajax$', 'assays.ajax.ajax'),
                       url(r'^compounds_ajax$', 'compounds.ajax.ajax'),
                       # END old-style API

                       url(r'^admin/doc/',
                           include('django.contrib.admindocs.urls')),
                       url(r'^admin/', include(admin.site.urls)),

)

# Note that the URL path can be whatever you want, but you must include
# rest_framework.urls' with the 'rest_framework' namespace.

urlpatterns += staticfiles_urlpatterns()

urlpatterns += patterns('',
                        url(r'^media/(?P<path>.*)$',
                            'django.views.static.serve', {
                                'document_root': settings.MEDIA_ROOT,
                            }),
)
