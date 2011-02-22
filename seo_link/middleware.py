import re

from django.core.exceptions import ImproperlyConfigured

from seo_link.models import ExcludePath
from seo_link.utils import get_seo_link_backend_class
from seo_link import settings
from django.conf import settings as django_settings

class SEOLinkMiddleware(object):
    """
    Middleware to inject links based on the term configuration
    
        add this before the csrf protection middleware and any other content manimulation middleware
    """
    backend = None
    
    def __init__(self,*args,**kwargs):
        # check if the csrf middleware is in the configrued middelwares
        if "django.middleware.csrf.CsrfViewMiddleware" in django_settings.MIDDLEWARE_CLASSES:
            # check if the middleware is before this middleware
            csrfId = django_settings.MIDDLEWARE_CLASSES.index('django.middleware.csrf.CsrfViewMiddleware')
            meId = django_settings.MIDDLEWARE_CLASSES.index('seo_link.middleware.SEOLinkMiddleware')
            if meId > csrfId:
                raise ImproperlyConfigured("SEOLinkMiddleware must be loaded before any Csrf Middleware, (internal Caching)")
        
        # check for misconfigurations
        if ((settings.OPERATIONAL_CSS_SELECTOR_CLASSES is None and 
             settings.OPERATIONAL_CSS_SELECTOR_IDS is None
             ) or 
             (settings.IGNORE_CSS_SELECTOR_CLASSES is None and
              settings.IGNORE_CSS_SELECTOR_IDS is None)
            ): 
            raise ImproperlyConfigured("ALL SEO_LINK_IGNORE_CSS_SELECTOR_* or All SEO_LINK_OPERATIONAL_CSS_SELECTOR_* are set to None")
        self.backend = get_seo_link_backend_class()
    
    def process_response(self, request, response):
        # do not operate on the root page
        if request.path == u"/":
            return response
        # ignore ajax and none 200er
        if request.is_ajax() or response.status_code != 200:
            return response
        # operate only on text/html
        if 'text/html' not in response['Content-Type']:
            return response
        # delegate to the backend
        if not settings.ACTIVE_ANONYMOUS_USER_ONLY:
            response=self.backend.process_response(request,response)
        if request.user.is_anonymous():
            response=self.backend.process_response(request,response)
        return response

    
        