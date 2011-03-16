# -*- coding: utf-8 -*-
from seo_link.admin.views import preview_url
from django.conf.urls.defaults import patterns, url
from seo_link.models import TestUrl

urlpatterns = patterns('',
                       url(r'^check/(?P<test_url_id>\d+)/$',      preview_url, name='seo_link_check_substitution'),
)
