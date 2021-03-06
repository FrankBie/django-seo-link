# -*- coding: utf-8 -*-
import time
import logging as log

from django.core.urlresolvers import reverse

import seo_link
import seo_link.settings as seo_link_settings
from seo_link.tests.base import SeoLinkTestCase
from seo_link.tests.mixins import ReplacementOneLinkPerTermMixin
from seo_link.tests.mixins import ReplacementMixin
from seo_link.tests.mixins import ReplacementNestingMixin
from seo_link.tests.mixins import OperatingPathMixin
from seo_link.tests.mixins import CachedMixin
    
from seo_link.utils import get_seo_link_backend_class



class ReplacementOneLinkPerTermTestCase(SeoLinkTestCase,ReplacementOneLinkPerTermMixin):
    def setUp(self):
        pass

class ReplacementTestCase(SeoLinkTestCase,ReplacementMixin):
    def setUp(self):
        pass


class ReplacementNestingTestCase(SeoLinkTestCase,ReplacementNestingMixin):
    def setUp(self):
        super(ReplacementNestingTestCase,self).setUp()
        import seo_link.settings as seo_link_settings
        
        self.OLD_IGNORE_CSS_SELECTOR_CLASSES = seo_link_settings.IGNORE_CSS_SELECTOR_CLASSES
        seo_link_settings.IGNORE_CSS_SELECTOR_CLASSES = ['nav','user-nav','footer','sidebar']
        
        self.OLD_OPERATIONAL_CSS_SELECTOR_CLASSES = seo_link_settings.OPERATIONAL_CSS_SELECTOR_CLASSES 
        seo_link_settings.OPERATIONAL_CSS_SELECTOR_CLASSES = ['main','main-content']
        self.OLD_OPERATIONAL_CSS_SELECTOR_IDS = seo_link_settings.OPERATIONAL_CSS_SELECTOR_IDS
        seo_link_settings.OPERATIONAL_CSS_SELECTOR_IDS = ['col3','col4']
        
        self.OLD_IGNORE_CSS_SELECTOR_IDS = seo_link_settings.IGNORE_CSS_SELECTOR_IDS
        seo_link_settings.IGNORE_CSS_SELECTOR_IDS = ['col2']
        
    def tearDown(self):
        super(ReplacementNestingTestCase,self).tearDown()
        import seo_link.settings as seo_link_settings
        seo_link_settings.IGNORE_CSS_SELECTOR_CLASSES = self.OLD_IGNORE_CSS_SELECTOR_CLASSES  
        seo_link_settings.OPERATIONAL_CSS_SELECTOR_CLASSES = self.OLD_OPERATIONAL_CSS_SELECTOR_CLASSES 
        seo_link_settings.OPERATIONAL_CSS_SELECTOR_IDS = self.OLD_OPERATIONAL_CSS_SELECTOR_IDS  
        seo_link_settings.IGNORE_CSS_SELECTOR_IDS = self.OLD_IGNORE_CSS_SELECTOR_IDS   


class OperatingPathTestCase(SeoLinkTestCase,OperatingPathMixin):
        pass    


class SimpleCachedBackendTestCase(SeoLinkTestCase,CachedMixin):
    def setUp(self):
        """ 
        Setup the cached backend
        """
        super(SimpleCachedBackendTestCase,self).setUp()
        seo_link_settings.BACKEND = "seo_link.backends.simple.SimpleCachedBackend"
        seo_link.middleware.SEO_BACKEND = get_seo_link_backend_class(path=seo_link_settings.BACKEND)
        
    
        