# coding=utf-8

"""
Bioactivities URL router
"""

from django.conf.urls import patterns, url

urlpatterns = patterns('bioactivities.views',
                       url(r'^bioactivities/$',
                           'bioactivities_list'),
                       url(r'^bioactivities/(?P<pk>[0-9]+)/$',
                           'bioactivities_detail'),
                       url(r'^bioactivities/all_bioactivities/$',
                           'list_of_all_bioactivities_in_bioactivities'),
                       url(r'^bioactivities/all_targets/$',
                           'list_of_all_targets_in_bioactivities'),
                       url(r'^bioactivities/all_compounds/$',
                           'list_of_all_compounds_in_bioactivities'),
                       url(r'^bioactivities/all_data/$',
                           'list_of_all_data_in_bioactivities'),
                       url(r'^bioactivities/gen_heatmap/$',
                           'gen_heatmap'),
                       )
