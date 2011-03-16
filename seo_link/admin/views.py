# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required

from django.core.urlresolvers import reverse

from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render_to_response
from django.template.context import RequestContext

from seo_link.models import TestUrl
from seo_link.settings import NO_PROCESSING_GET_PARAM, PREVIEW_TEST_URL_PREFIX


def login_required(func):
    
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseRedirect(reverse('admin-login'))
            
        return func(request, *args, **kwargs)
    wrapped.__doc__ = func.__doc__
    wrapped.__name__ = func.__name__
    return wrapped


def preview_url(request,test_url_id):
    test_url=u"" 
    test_url_no_processing =u""
    sep = u"?"
    test_url_obj = TestUrl.objects.get(id=test_url_id)
    if test_url_obj:
        test_url=u"%s%s" % (PREVIEW_TEST_URL_PREFIX,test_url_obj.test_url)
        if test_url.find("?")!=-1: 
            sep=u"&"
        test_url_no_processing = u"%s%s%s=True" %(test_url,sep,NO_PROCESSING_GET_PARAM)
        
    return render_to_response('seo_link/admin/substitution.html', locals(), context_instance=RequestContext(request))