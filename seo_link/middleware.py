# -*- coding: utf-8 -*-
import re
import logging as log

from django.core.exceptions import ImproperlyConfigured
from django.conf import settings as django_settings

from seo_link import settings
from seo_link.utils import get_seo_link_backend_class


# one instance of the seo_backend only
# Singleton
SEO_BACKEND = None
if SEO_BACKEND is None:
    log.warn("SEO_BACKEND loaded - middleware")
    SEO_BACKEND = get_seo_link_backend_class()
    
class SEOLinkMiddleware(object):
    """
    Middleware to inject links based on the term configuration
    add this before the csrf protection middleware and any other content manipulation middlewares
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
        if ("django.middleware.csrf.CsrfResponseMiddleware" in django_settings.MIDDLEWARE_CLASSES):
                csrfId = django_settings.MIDDLEWARE_CLASSES.index('django.middleware.csrf.CsrfResponseMiddleware')
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
        self.backend = SEO_BACKEND
        # on startup clear the stored cache keys
        #if instanceof(self.backend,AbstractCachedMixin):
        #    self.backend.clear_cached()
    
    def process_response(self, request, response):
        if response.status_code != 200:
            return response
        # do not operate on the root page 
        if settings.NO_ROOT_PROCESSING and request.path == u"/":
            return response
        
        # global ignores
        global_ignore=False
        for ignore_path in settings.GLOBAL_EXCLUDE_PATHES:
            global_ignore = (unicode(request.path).find(ignore_path) == 0) 
            if global_ignore:
                break
        if global_ignore:
            return response
        # ignore ajax
        if request.is_ajax():
            return response
        
        # operate only on text/html
        if 'text/html' not in response['Content-Type']:
            return response
        
        # delegate to the backend
        # and ensure that the site
        # gets not broken in case of any error
        if not settings.IGNORE_EXCEPTIONS_ON:
                if not settings.ACTIVE_ANONYMOUS_USER_ONLY:
                    response=self.backend.process_response(request,response)
                if request.user.is_anonymous() and settings.ACTIVE_ANONYMOUS_USER_ONLY:
                    response=self.backend.process_response(request,response)
        else:
            response_content_backup=None
            try: 
                response_content_backup=response.content
                if not settings.ACTIVE_ANONYMOUS_USER_ONLY:
                    response=self.backend.process_response(request,response)
                if request.user.is_anonymous() and settings.ACTIVE_ANONYMOUS_USER_ONLY:
                    response=self.backend.process_response(request,response)
            except Exception,e:
                msg = u"SEOLinkMiddleware error at %s unparseable content" %(request.get_full_path())
                log.error(msg)
                log.error(e.msg)
                response.content = response_content_backup
        
        return response
