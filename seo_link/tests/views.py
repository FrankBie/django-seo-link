# -*- coding: utf-8 -*-
from django.template.context import RequestContext
from django.shortcuts import render_to_response




def view_testpage_1(request):
    import seo_link.settings as seo_link_settings
    from seo_link.middleware import SEO_BACKEND
    return render_to_response('seo_link/tests/testpage_1.html', locals(), context_instance=RequestContext(request))

def view_testpage_2(request):
    import seo_link.settings as seo_link_settings
    from seo_link.middleware import SEO_BACKEND
    return render_to_response('seo_link/tests/testpage_2.html', locals(), context_instance=RequestContext(request))

def view_testpage_3(request):
    # nesting test
    import seo_link.settings as seo_link_settings
    from seo_link.middleware import SEO_BACKEND
    seo_link_settings.IGNORE_CSS_SELECTOR_CLASSES = ['nav','user-nav','footer','sidebar']
    seo_link_settings.OPERATIONAL_CSS_SELECTOR_CLASSES = ['main','main-content']
    seo_link_settings.OPERATIONAL_CSS_SELECTOR_IDS = ['col3','col4']
    seo_link_settings.IGNORE_CSS_SELECTOR_IDS = ['col2']
    
    return render_to_response('seo_link/tests/testpage_3.html', locals(), context_instance=RequestContext(request))

def view_testpage_4(request):
    import seo_link.settings as seo_link_settings
    from seo_link.middleware import SEO_BACKEND
    #@todo: add a form to the layout to check if the csrf is working with post data
    return render_to_response('seo_link/tests/testpage_4.html', locals(), context_instance=RequestContext(request))

def view_testpage_5(request):
    import seo_link.settings as seo_link_settings
    from seo_link.middleware import SEO_BACKEND
    #@todo: add a form to the layout to check if the csrf is working with post data
    return render_to_response('seo_link/tests/testpage_5.html', locals(), context_instance=RequestContext(request))

def view_testpage_6(request):
    
    import seo_link.settings as seo_link_settings
    from seo_link.middleware import SEO_BACKEND
    return render_to_response('seo_link/tests/testpage_6.html', locals(), context_instance=RequestContext(request))

def view_testpage_7(request):
    """
    Broken BR TAGS
    """
    import seo_link.settings as seo_link_settings
    from seo_link.middleware import SEO_BACKEND
    return render_to_response('seo_link/tests/testpage_7.html', locals(), context_instance=RequestContext(request))

def view_testpage_reg_ex_abc(request):
    import seo_link.settings as seo_link_settings
    from seo_link.middleware import SEO_BACKEND
    #SEO_BACKEND.clear_related_terms_per_page_cache()
    return render_to_response('seo_link/tests/testpage_reg_ex_abc.html', locals(), context_instance=RequestContext(request))

def view_testpage_reg_ex_abcdef(request):
    import seo_link.settings as seo_link_settings
    from seo_link.middleware import SEO_BACKEND
    #SEO_BACKEND.clear_related_terms_per_page_cache()
    return render_to_response('seo_link/tests/testpage_reg_ex_abcdef.html', locals(), context_instance=RequestContext(request))
