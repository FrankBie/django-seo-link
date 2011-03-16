# -*- coding: utf-8 -*-
import logging as log

from django.db.models.signals import post_save

import seo_link
from seo_link.backends import AbstractUtilsMixin, OperationalCacheMixin
from seo_link.models import Term, OperatingPath, ReplacementTemplate
import seo_link.settings as seo_link_settings


# signals for fireing the clear cache events
def drop_cache_related_terms_per_page(sender, instance, **kwargs):
    """
    Just drops the term page cache of the currently configured backend
    """ 
    backend = seo_link.middleware.SEO_BACKEND
    if isinstance(backend,AbstractUtilsMixin):
        backend.clear_related_terms_per_page_cache()
        if seo_link_settings.DEBUG:
            log.debug("Dropped related terms cache by signal %s " % instance)

post_save.connect(drop_cache_related_terms_per_page, sender=Term)
post_save.connect(drop_cache_related_terms_per_page, sender=OperatingPath)
post_save.connect(drop_cache_related_terms_per_page, sender=ReplacementTemplate)

def drop_cached_processed_pages(sender, instance, **kwargs):
    """
    Just processed pages cache of the currently configured backend
    """ 
    backend = seo_link.middleware.SEO_BACKEND
    if isinstance(backend,OperationalCacheMixin):
        backend.clear_cached()
        if seo_link_settings.DEBUG:
            log.debug("Dropped processed pages cache by signal %s " % instance)
    
post_save.connect(drop_cached_processed_pages, sender=Term)
post_save.connect(drop_cached_processed_pages, sender=OperatingPath)
