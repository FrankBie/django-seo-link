# -*- coding: utf-8 -*-
import time
import logging as log

from django.core.urlresolvers import reverse
from django.test.testcases import TestCase

import seo_link.settings as seo_link_settings
from BeautifulSoup import BeautifulSoup

class ReplacementMixin(TestCase): 
    
    def test_process_testpage1_replacement_working(self):
        """
        process testpage 1
        """
        log.debug("test_process_testpage1_replacement_working: cls: %s"%(self))
        url = reverse("seo_link_testpage_1")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # make the content human readable
        response.content = BeautifulSoup(response.content).prettify()
        
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
        # allowed html tags test
        self.assertContains(response, 'h1 never replaced test_me')
        self.assertContains(response, 'h2 never replaced test_me')
        self.assertContains(response, 'bold never replaced test_me')
        self.assertContains(response, 'a never replaced ###REPLACE ME### LINK')

    def test_process_testpage2(self):
        url = reverse("seo_link_testpage_2")
        response = self.client.get(url)
        response.content = BeautifulSoup(response.content).prettify()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'a never replaced ###REPLACE ME### LINK')
        
class ReplacementOneLinkPerTermMixin(TestCase):
    
    def test_one_link_per_term(self):
        """
        process testpage 1
        """
        log.debug("%s.test_one_link_per_term"%(self))
        url = reverse("seo_link_testpage_1")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response.content = BeautifulSoup(response.content).prettify()
        # test if the ###always ignore term is in the page
        # he should contain it
        self.assertContains(response, 'and this text should never be replaced ###REPLACE ME###')

class ReplacementNestingMixin(TestCase):
    
    def test_nesting(self):
        # sidebar ignored
        # col2 ignored
        # col3/ col4 operational
        log.debug("%s.test_nesting"%(self))
        url = reverse("seo_link_testpage_3")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response.content = BeautifulSoup(response.content).prettify()
        # test if the ignore combinations work
        self.assertDumpContains(response, url, 'not be replaced col1 sidebar ###REPLACE ME###')
        self.assertDumpContains(response, url, 'not be replaced col2-ignore-main ###REPLACE ME###')
        self.assertDumpContains(response, url, 'not be replaced main-col3-sidebar-ignore ###REPLACE ME###')
        self.assertDumpContains(response, url, 'not be replaced col4-sidebar-ignore ###REPLACE ME###')
        # operational combinations
        self.assertDumpContains(response, url, """here it should be replaced main-content
         <span class="seo-link red">
          / TEST_TEMPLATE ###REPLACE ME###
         </span>""")
        self.assertDumpContains(response, url, """here it should be replaced main-content second
         <span class="seo-link red">
          / TEST_TEMPLATE ###REPLACE ME###
         </span>""")
        self.assertDumpContains(response, url, """id=col3 is operational, so this should be replaced main-col3
        <span class="seo-link red">
         / TEST_TEMPLATE ###REPLACE ME###
        </span>""")
        self.assertDumpContains(response, url, """so this should be replaced main-col4
        <span class="seo-link red">
         / TEST_TEMPLATE ###REPLACE ME###""")


class OperatingPathMixin(TestCase):
    """
    Tests if the operating path configurations work
    """
    def test_path_startswith(self):
        url = reverse("seo_link_testpage_reg_ex_abc")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response.content = BeautifulSoup(response.content).prettify()
        self.assertDumpContains(response, url, """/ TEST_TEMPLATE ###STARTS_WITH###""")
        
        self.assertDumpContains(response, url, """
        """)
    
    def test_path_exact(self):
        # assumes /link/....
        url = reverse("seo_link_testpage_reg_ex_abc")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response.content = BeautifulSoup(response.content).prettify()
        self.assertDumpContains(response, url, """TEST_TEMPLATE ###EXACT###""")        

    def test_path_reg_ex(self):
        url = reverse("seo_link_testpage_reg_ex_abc")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response.content = BeautifulSoup(response.content).prettify()
        self.assertDumpContains(response, url, """/ TEST_TEMPLATE ###REG_EX###""")
        
    def test_include_path_contains(self):
        url = reverse("seo_link_testpage_reg_ex_abc")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response.content = BeautifulSoup(response.content).prettify()
        self.assertDumpContains(response, url,"""/ TEST_TEMPLATE ###CONTAINS_ABC###""")
        self.assertDumpContains(response, url,"""</b>
     ###CONTAINS_DEF###""")
        self.assertDumpContains(response, url,"""/ TEST_TEMPLATE test_me""")
        
        
    def test_path_contains_not(self):
        """
        process testpage 1
        """
        url = reverse("seo_link_testpage_reg_ex_abcdef")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response.content = BeautifulSoup(response.content).prettify()
        self.assertDumpContains(response, url,"""<b>
      def
     </b>
     ###CONTAINS_DEF###
    </p>""")
            
            
class CachedMixin(TestCase):
    def process_url(self, url):
        from seo_link.middleware import SEO_BACKEND
        start_time = time.clock()
        response = self.client.get(url)
        processing_time = time.clock() - start_time
        log.debug("url: %s ptime: %s backend: %s active backend: %s" % (url,processing_time,seo_link_settings.BACKEND,SEO_BACKEND))
        return processing_time, response
    
    def test_caching(self):
        url = reverse("seo_link_testpage_3")
        processing_time,response = self.process_url(url)
        self.assertEqual(response.status_code, 200)
        cached_processing_time,response = self.process_url(url)
        response.content = BeautifulSoup(response.content).prettify()
        self.assertDumpContains(response, url,"""cached processing time""")
        self.assertFalse(cached_processing_time >1.0)
        cached_processing_time,response = self.process_url(url)
        self.assertFalse(cached_processing_time >0.8)
        cached_processing_time,response = self.process_url(url)
        self.assertFalse(cached_processing_time >0.4)
        cached_processing_time,response = self.process_url(url)
        self.assertFalse(cached_processing_time >0.1)
        
        url = reverse("seo_link_testpage_2")
        processing_time,response = self.process_url(url)
        self.assertEqual(response.status_code, 200)
        cached_processing_time,response = self.process_url(url)
        response.content = BeautifulSoup(response.content).prettify()
        self.assertDumpContains(response, url,"""cached processing time""")
        
        self.assertFalse(cached_processing_time >0.4)
        
        url = reverse("seo_link_testpage_1")
        processing_time,response = self.process_url(url)
        self.assertEqual(response.status_code, 200)
        cached_processing_time,response = self.process_url(url)
        response.content = BeautifulSoup(response.content).prettify()
        self.assertDumpContains(response, url,"""cached processing time""")
        self.assertFalse(cached_processing_time >0.4)
