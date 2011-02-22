from django.template.context import RequestContext
from django.shortcuts import render_to_response


def view_testpage_1(request):
    import seo_link.settings as seo_link_settings
    return render_to_response('seo_link/tests/testpage_1.html', locals(), context_instance=RequestContext(request))

def view_testpage_2(request):
    import seo_link.settings as seo_link_settings
    return render_to_response('seo_link/tests/testpage_2.html', locals(), context_instance=RequestContext(request))

def view_testpage_3(request):
    # nesting test
    import seo_link.settings as seo_link_settings
    seo_link_settings.IGNORE_CSS_SELECTOR_CLASSES = ['nav','user-nav','footer','sidebar']
    seo_link_settings.OPERATIONAL_CSS_SELECTOR_CLASSES = ['main','main-content']
    seo_link_settings.OPERATIONAL_CSS_SELECTOR_IDS = ['col3','col4']
    seo_link_settings.IGNORE_CSS_SELECTOR_IDS = ['col2']
    return render_to_response('seo_link/tests/testpage_3.html', locals(), context_instance=RequestContext(request))

def view_testpage_4(request):
    #@todo: add a form to the layout to check if the csrf is working with post data
    
    return render_to_response('seo_link/tests/testpage_3.html', locals(), context_instance=RequestContext(request))