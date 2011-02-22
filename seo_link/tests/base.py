# -*- coding: utf-8 -*-
import sys
import warnings

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.handlers.wsgi import WSGIRequest
from django.test.testcases import TestCase


class _Warning(object):
    def __init__(self, message, category, filename, lineno):
        self.message = message
        self.category = category
        self.filename = filename
        self.lineno = lineno

def _collectWarnings(observeWarning, f, *args, **kwargs):
    def showWarning(message, category, filename, lineno, file=None, line=None):
        assert isinstance(message, Warning)
        observeWarning(_Warning(
                message.args[0], category, filename, lineno))

    # Disable the per-module cache for every module otherwise if the warning
    # which the caller is expecting us to collect was already emitted it won't
    # be re-emitted by the call to f which happens below.
    for v in sys.modules.itervalues():
        if v is not None:
            try:
                v.__warningregistry__ = None
            except:
                # Don't specify a particular exception type to handle in case
                # some wacky object raises some wacky exception in response to
                # the setattr attempt.
                pass

    origFilters = warnings.filters[:]
    origShow = warnings.showwarning
    warnings.simplefilter('always')
    try:
        warnings.showwarning = showWarning
        result = f(*args, **kwargs)
    finally:
        warnings.filters[:] = origFilters
        warnings.showwarning = origShow
    return result

class SeoLinkTestCase(TestCase):
    counter = 1
        
    def _pre_setup(self):
        """We are doing a lot of setting modifications in our tests, this 
        mechanism will restore to original settings after each test case.
        """
        super(SeoLinkTestCase, self)._pre_setup()
        # backup settings
        #self._original_settings_wrapped = copy.deepcopy(settings._wrapped) 
        
    def _post_teardown(self):
        # restore original settings after each test
        #settings._wrapped = self._original_settings_wrapped
        super(SeoLinkTestCase, self)._post_teardown()
    
    def login_user(self, user):
        logged_in = self.client.login(username=user.username, password=user.username)
        self.user = user
        self.assertEqual(logged_in, True)
        
    def logout_user(self):
        logged_out = self.client.logout()
        self.user = None
        
    def setup_admin_user(self, uname):
        u = self.setup_normal_user(uname)
        u.is_staff = True
        u.is_active = True
        u.is_superuser = True
        u.save()
        return u

    def setup_normal_user(self, uname):
        u = User(username=uname, is_staff=False, is_active=True, is_superuser=False)
        u.set_password(uname)
        u.save()
        return u

    def assertObjectExist(self, qs, **filter):
        try:
            return qs.get(**filter) 
        except ObjectDoesNotExist:
            pass
        raise self.failureException, "ObjectDoesNotExist raised"
    
    def assertObjectDoesNotExist(self, qs, **filter):
        try:
            qs.get(**filter) 
        except ObjectDoesNotExist:
            return
        raise self.failureException, "ObjectDoesNotExist not raised"
    
    def get_context(self, path="/"):
        context = {}
        request = self.get_request(path)
        
        context['request'] = request
        
        return context   
        
    def get_request(self, path="/"):
        environ = {
            'HTTP_COOKIE':      self.client.cookies,
            'PATH_INFO':         path,
            'QUERY_STRING':      '',
            'REMOTE_ADDR':       '127.0.0.1',
            'REQUEST_METHOD':    'GET',
            'SCRIPT_NAME':       '',
            'SERVER_NAME':       'testserver',
            'SERVER_PORT':       '80',
            'SERVER_PROTOCOL':   'HTTP/1.1',
            'wsgi.version':      (1, 0),
            'wsgi.url_scheme':   'http',
            'wsgi.errors':       self.client.errors,
            'wsgi.multiprocess': True,
            'wsgi.multithread':  False,
            'wsgi.run_once':     False,
        }
        request = WSGIRequest(environ)
        request.session = self.client.session
        request.user = self.user
        request.LANGUAGE_CODE = settings.LANGUAGES[0][0]
        return request
        
        
    def failUnlessWarns(self, category, message, f, *args, **kwargs):
        warningsShown = []
        result = _collectWarnings(warningsShown.append, f, *args, **kwargs)

        if not warningsShown:
            self.fail("No warnings emitted")
        first = warningsShown[0]
        for other in warningsShown[1:]:
            if ((other.message, other.category)
                != (first.message, first.category)):
                self.fail("Can't handle different warnings")
        self.assertEqual(first.message, message)
        self.assertTrue(first.category is category)

        return result
    assertWarns = failUnlessWarns
