from django.conf.urls import url
import qhonuskan_votes.views

urlpatterns = [
    url(r'^vote/$', qhonuskan_votes.views.vote, name='qhonuskan_vote')
]

