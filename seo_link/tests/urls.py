# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

from seo_link.tests.views import  view_testpage_1, view_testpage_2,\
    view_testpage_3,view_testpage_4,view_testpage_5,view_testpage_6,view_testpage_7,\
    view_testpage_reg_ex_abc, view_testpage_reg_ex_abcdef

urlpatterns = patterns('')
urlpatterns += patterns('',
        url(r'^testpage-1/$', view_testpage_1, name='seo_link_testpage_1'),
        url(r'^testpage-2/$', view_testpage_2, name='seo_link_testpage_2'),
        url(r'^testpage-3/$', view_testpage_3, name='seo_link_testpage_3'),
        url(r'^testpage-4/$', view_testpage_4, name='seo_link_testpage_4'),
        url(r'^testpage-5/$', view_testpage_5, name='seo_link_testpage_5'),
        url(r'^testpage-6/$', view_testpage_6, name='seo_link_testpage_6'),
        url(r'^testpage-7/$', view_testpage_7, name='seo_link_testpage_7'),
        url(r'^testpage-reg-ex-abc/$', view_testpage_reg_ex_abc, name='seo_link_testpage_reg_ex_abc'),
        url(r'^testpage-reg-ex-abcdef/$', view_testpage_reg_ex_abcdef, name='seo_link_testpage_reg_ex_abcdef'),
)
