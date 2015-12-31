"""
URL routing patterns for the Deis project.

This is the "master" urls.py which then includes the urls.py files of
installed apps.
"""

from __future__ import unicode_literals

from django.conf.urls import patterns, include, url
from api.views import HealthCheckView

urlpatterns = patterns(
    '',
    url(r'^health-check$', HealthCheckView.as_view()),
    url(r'^v2/', include('api.urls')),
)
