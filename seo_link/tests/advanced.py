# -*- coding: utf-8 -*-

import logging as log
import seo_link
from seo_link.utils import get_seo_link_backend_class

from seo_link.tests.base import SeoLinkTestCase
from seo_link.tests.mixins import ReplacementMixin,\
    ReplacementOneLinkPerTermMixin, ReplacementNestingMixin, OperatingPathMixin,\
    CachedMixin




class LxmlTestCase(SeoLinkTestCase):
    def setUp(self):
        import seo_link.settings as seo_link_settings
        seo_link_settings.IGNORE_CSS_SELECTOR_CLASSES = ['nav','user-nav','footer','sidebar']
        seo_link_settings.OPERATIONAL_CSS_SELECTOR_CLASSES = ['main']
        seo_link_settings.OPERATIONAL_CSS_SELECTOR_IDS = None
        seo_link_settings.IGNORE_CSS_SELECTOR_IDS = None
        seo_link_settings.BACKEND = "seo_link.backends.advanced.LXMLBackend"
        seo_link.middleware.SEO_BACKEND = get_seo_link_backend_class(path=seo_link_settings.BACKEND)
    

class LxmlReplacementOneLinkPerTermTestCase(LxmlTestCase,ReplacementOneLinkPerTermMixin):
    pass
    

class LxmlReplacementTestCase(LxmlTestCase,ReplacementMixin):
    pass


class LxmlReplacementNestingTestCase(LxmlTestCase,ReplacementNestingMixin):
    def setUp(self):
        import seo_link.settings as seo_link_settings
        
        super(LxmlReplacementNestingTestCase,self).setUp()
        
        self.OLD_IGNORE_CSS_SELECTOR_CLASSES = seo_link_settings.IGNORE_CSS_SELECTOR_CLASSES
        seo_link_settings.IGNORE_CSS_SELECTOR_CLASSES = ['nav','user-nav','footer','sidebar']
        
        self.OLD_OPERATIONAL_CSS_SELECTOR_CLASSES = seo_link_settings.OPERATIONAL_CSS_SELECTOR_CLASSES 
        seo_link_settings.OPERATIONAL_CSS_SELECTOR_CLASSES = ['main','main-content']
        self.OLD_OPERATIONAL_CSS_SELECTOR_IDS = seo_link_settings.OPERATIONAL_CSS_SELECTOR_IDS
        seo_link_settings.OPERATIONAL_CSS_SELECTOR_IDS = ['col3','col4']
        
        self.OLD_IGNORE_CSS_SELECTOR_IDS = seo_link_settings.IGNORE_CSS_SELECTOR_IDS
        seo_link_settings.IGNORE_CSS_SELECTOR_IDS = ['col2']
        
        
    def tearDown(self):
        import seo_link.settings as seo_link_settings
        super(LxmlReplacementNestingTestCase,self).tearDown()
        seo_link_settings.IGNORE_CSS_SELECTOR_CLASSES = self.OLD_IGNORE_CSS_SELECTOR_CLASSES  
        seo_link_settings.OPERATIONAL_CSS_SELECTOR_CLASSES = self.OLD_OPERATIONAL_CSS_SELECTOR_CLASSES 
        seo_link_settings.OPERATIONAL_CSS_SELECTOR_IDS = self.OLD_OPERATIONAL_CSS_SELECTOR_IDS  
        seo_link_settings.IGNORE_CSS_SELECTOR_IDS = self.OLD_IGNORE_CSS_SELECTOR_IDS   
        

class LxmlOperatingPathTestCase(LxmlTestCase,OperatingPathMixin):
        pass     
    
class LxmlCachedBackendTestCase(LxmlTestCase,CachedMixin):
    
    def setUp(self):
        """ 
        Setup the cached backend
        """
        import seo_link.settings as seo_link_settings
        seo_link_settings.BACKEND = "seo_link.backends.advanced.LXMLCachedBackend"
        seo_link.middleware.SEO_BACKEND = get_seo_link_backend_class(path=seo_link_settings.BACKEND)
        

    