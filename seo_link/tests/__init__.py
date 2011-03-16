# -*- coding: utf-8 -*-
import unittest
import doctest

from django.test.simple import run_tests as django_test_runner
from seo_link.tests.advanced import *
from seo_link.tests.backend import *
    


    
  
#
def suite():
    s = unittest.TestSuite()
    #BACKEND = getattr(django_settings, 'SEO_LINK_BACKEND','seo_link.backends.simple.SimpleBackend')
    s.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(ReplacementNestingTestCase))
    s.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(ReplacementTestCase))
    s.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(OperatingPathTestCase))
    #lxml
    #BACKEND = getattr(django_settings, 'SEO_LINK_BACKEND','seo_link.backends.advanced.LXMLBackend')
    s.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(LxmlReplacementNestingTestCase))
    s.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(LxmlReplacementTestCase))
    s.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(LxmlOperatingPathTestCase))
    #BACKEND = getattr(django_settings, 'SEO_LINK_BACKEND','seo_link.backends.simple.SimpleCachedBackend')
    s.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(SimpleCachedBackendTestCase))
    #BACKEND = getattr(django_settings, 'SEO_LINK_BACKEND','seo_link.backends.advanced.LXMLCachedBackend')
    s.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(LxmlCachedBackendTestCase))
    
    return s
 
def test_runner_with_coverage(test_labels, verbosity=1, interactive=True, extra_tests=[]):
    """Custom test runner.  Follows the django.test.simple.run_tests() interface."""
    import os, shutil, sys

    # Look for coverage.py in __file__/lib as well as sys.path
    sys.path = [os.path.join(os.path.dirname(__file__), "lib")] + sys.path
     
    import coverage
    from django.test.simple import run_tests as django_test_runner
     
    from django.conf import settings
    
    # Start code coverage before anything else if necessary
    #if hasattr(settings, 'COVERAGE_MODULES') and not test_labels:
    coverage.use_cache(0) # Do not cache any of the coverage.py stuff
    coverage.start()

    test_results = django_test_runner(test_labels, verbosity, interactive, extra_tests)

    # Stop code coverage after tests have completed
    #if hasattr(settings, 'COVERAGE_MODULES') and not test_labels:
    coverage.stop()

    # Print code metrics header
    print ''
    print '----------------------------------------------------------------------'
    print ' Unit Test Code Coverage Results'
    print '----------------------------------------------------------------------'

    # Report code coverage metrics
    coverage_modules = []
    if hasattr(settings, 'COVERAGE_MODULES') and (not test_labels):
        for module in settings.COVERAGE_MODULES:
            coverage_modules.append(__import__(module, globals(), locals(), ['']))
    coverage.report(coverage_modules, show_missing=1)
            #Print code metrics footer
    print '----------------------------------------------------------------------'

    return test_results
