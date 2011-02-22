from seo_link.tests.base import SeoLinkTestCase
from django.core.urlresolvers import reverse
import time
import logging as log

class ReplacementOneLinkPerTermTestCase(SeoLinkTestCase):
    
    def setUp(self):
        
        pass

    def test_one_link_per_term(self):
        """
        process testpage 1
        """
        url = reverse("seo_link_testpage_1")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # test if the ###always ignore term is in the page
        # he should contain it
        self.assertContains(response, 'and this text should never be replaced ###REPLACE ME###')
    

class ReplacementTestCase(SeoLinkTestCase):
    
    def setUp(self):
        pass

    def test_process_testpage1_replacement_working(self):
        """
        process testpage 1
        """
        url = reverse("seo_link_testpage_1")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # test if the ###always ignore term is in the page
        # he should contain it
        self.assertContains(response, 'and this text should never be replaced ###REPLACE ME###')
        #5 words ignore pattern
        
        self.assertContains(response, 'TEST_TEMPLATE test_me')
        self.assertContains(response, 'TEST_TEMPLATE test me')
        self.assertContains(response, 'TEST_TEMPLATE test me now')
        self.assertContains(response, 'TEST_TEMPLATE test me now here')
        self.assertContains(response, 'TEST_TEMPLATE test me now here fast')
        
        
        self.assertNotContains(response,'wordcount 1 test_me')
        self.assertNotContains(response,'wordcount 2 test me')
        self.assertNotContains(response,'wordcount 3 test me now')
        self.assertNotContains(response,'wordcount 4 test me now here')
        self.assertNotContains(response,'wordcount 5 test me now here fast')
        
        self.assertContains(response, 'h1 never replaced test_me')
        self.assertContains(response, 'h2 never replaced test_me')
        self.assertContains(response, 'bold never replaced test_me')
        self.assertContains(response, 'a never replaced ###REPLACE ME### LINK')

    def test_process_testpage2(self):
        """
        process testpage 1
        """
        url = reverse("seo_link_testpage_2")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'a never replaced ###REPLACE ME### LINK')


class ExcludePathTestCases(SeoLinkTestCase):
    
    def setUp(self):
        pass

    def test_model_exclude_path_regex(self):
        """
        process testpage 1
        """
        url = reverse("seo_link_testpage_3")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        pass

    def test_model_exclude_path_startswith(self):
        """
        process testpage 1
        """
        url = reverse("seo_link_testpage_3")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        pass

    def test_model_exclude_path_exact(self):
        """
        process testpage 1
        """
        url = reverse("seo_link_testpage_3")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        pass


class ReplacementNestingTestCase(SeoLinkTestCase):
    
    def setUp(self):
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
        import seo_link.settings as seo_link_settings
        
        seo_link_settings.IGNORE_CSS_SELECTOR_CLASSES = self.OLD_IGNORE_CSS_SELECTOR_CLASSES  
        seo_link_settings.OPERATIONAL_CSS_SELECTOR_CLASSES = self.OLD_OPERATIONAL_CSS_SELECTOR_CLASSES 
        seo_link_settings.OPERATIONAL_CSS_SELECTOR_IDS = self.OLD_OPERATIONAL_CSS_SELECTOR_IDS  
        seo_link_settings.IGNORE_CSS_SELECTOR_IDS = self.OLD_IGNORE_CSS_SELECTOR_IDS   
        
    def test_nesting(self):
        url = reverse("seo_link_testpage_3")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # test if the ignore combinations work
        self.assertContains(response, 'not be replaced col1 sidebar ###REPLACE ME###')
        self.assertContains(response, 'not be replaced col2-ignore-main ###REPLACE ME###')
        self.assertContains(response, 'not be replaced main-col3-sidebar-ignore ###REPLACE ME###')
        self.assertContains(response, 'not be replaced col4-sidebar-ignore ###REPLACE ME###')
        # operational combinations
        self.assertContains(response, """here it should be replaced main-content
         <span class=\"seo-link red\">
          / TEST_TEMPLATE ###REPLACE ME###
         </span>""")

        self.assertContains(response, """here it should be replaced main-content second
         <span class=\"seo-link red\">
          / TEST_TEMPLATE ###REPLACE ME###
         </span>""")

        self.assertContains(response, """so this should be replaced main-col3
        <span class=\"seo-link red\">
         / TEST_TEMPLATE ###REPLACE ME###
        </span>""")
        self.assertContains(response, """so this should be replaced main-col4
        <span class=\"seo-link red\">
         / TEST_TEMPLATE ###REPLACE ME###
        </span>""")



        
class SimpleCachedBackendTestCase(SeoLinkTestCase):
    
    
    def setUp(self):
        import seo_link.settings as seo_link_settings
        self.old_backend = seo_link_settings.BACKEND 
        seo_link_settings.BACKEND = "seo_link.backends.simple.SimpleCachedBackend"
        
    
    def tearDown(self):
        import seo_link.settings as seo_link_settings
        seo_link_settings.BACKEND = self.old_backend
    
    
    def process_url(self, url):
        start_time = time.clock()
        response = self.client.get(url)
        processing_time = time.clock() - start_time
        log.debug("url: %s, processing_time %s" % (url,processing_time))
        return processing_time, response
    
    def test_caching(self):
        url = reverse("seo_link_testpage_3")
        processing_time,response = self.process_url(url)
        self.assertEqual(response.status_code, 200)
        cached_processing_time,response = self.process_url(url)
        self.assertFalse(cached_processing_time >0.2)
        
        url = reverse("seo_link_testpage_2")
        processing_time,response = self.process_url(url)
        self.assertEqual(response.status_code, 200)
        cached_processing_time,response = self.process_url(url)
        self.assertFalse(cached_processing_time >0.2)
        
        url = reverse("seo_link_testpage_1")
        processing_time,response = self.process_url(url)
        self.assertEqual(response.status_code, 200)
        cached_processing_time,response = self.process_url(url)
        self.assertFalse(cached_processing_time >0.2)
         