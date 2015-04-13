from django.conf.urls import patterns, url

urlpatterns = patterns(
    'qhonuskan_votes.views',

    url(r'^vote/$', view='vote', name='qhonuskan_vote'))
