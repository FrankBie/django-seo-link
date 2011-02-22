from django.conf.urls.defaults import patterns, url

from seo_link.tests.views import  view_testpage_1, view_testpage_2,\
    view_testpage_3,view_testpage_4

urlpatterns = patterns('')
urlpatterns += patterns('',
        url(r'^testpage-1/$', view_testpage_1, name='seo_link_testpage_1'),
        url(r'^testpage-2/$', view_testpage_2, name='seo_link_testpage_2'),
        url(r'^testpage-3/$', view_testpage_3, name='seo_link_testpage_3'),
        url(r'^testpage-3/$', view_testpage_4, name='seo_link_testpage_4'),
)
