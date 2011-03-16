# -*- coding: utf-8 -*-
import hashlib
import logging as log
import re
import urllib2
import os
import socket

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.handlers.wsgi import WSGIRequest
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module
from django.utils import encoding
from django.test.client import Client

from seo_link import settings as seo_link_setting
from BeautifulSoup import UnicodeDammit


def get_seo_link_backend_class(path=None):
    """
    Return an instance of a seo_link_BACKEND backend, given the dotted
    Python import path (as a string) to the backend class.

    If the backend cannot be located (e.g., because no such module
    exists, or because the module does not contain a class of the
    appropriate name), ``django.core.exceptions.ImproperlyConfigured``
    is raised.
    
    This Method uses the Setting seo_link_BACKEND to plug play another backend
    
    """
    
    if path is None:
        # get the value from the settings
        path = seo_link_setting.BACKEND  
        msg="Configured seo_link_BACKEND Backend: %s" % (path)
        log.debug(msg)
    
    i = path.rfind('.')
    module, attr = path[:i], path[i+1:]
    try:
        mod = import_module(module)
    except ImportError, e:
        raise ImproperlyConfigured('Error loading seo_link_BACKEND backend %s: "%s"' % (module, e))
    try:
        backend_class = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define seo_link_BACKEND backend named "%s"' % (module, attr))
    return backend_class()


def get_md5_to_content(the_page):
    """
    Generate an md5 to the_page and remove csrfmiddlewaretoken for the calculation
    Purpose:
        Caching
        Test Comparism
    """
    lines = the_page.split("\n")
    out = u""
    r = re.compile("^.*[\'|\"]csrfmiddlewaretoken[\'|\"] value=[\'|\"](.*)[\'|\"].*$")
    for line in lines:
        rex = r.match(line)
        if rex is not None:
            line = line.replace(rex.groups()[0], "1234")
        out = out + line + "\n"
    md5_str = hashlib.md5(out).hexdigest()
    return (out , md5_str)
    
def flatten_tags(s, tags):
    pattern = re.compile(r"<(( )*|/?)(%s)(([^<>]*=\\\".*\\\")*|[^<>]*)/?>"%(isinstance(tags, basestring) and tags or "|".join(tags)))
    return pattern.sub("", s)

def removeNL(x):
    """cleans a string of new lines and spaces"""
    s = x.split('\n')
    s = [x.strip() for x in s]
    x = " ".join(s)
    return x.lstrip()

 
class DummyClient(object):
    """
    Dummy client for the admin test url page
    """
    
    def __init__(self,*args,**kwargs):
        self.client = Client()
        self.user = AnonymousUser() 
    
    def set_user (self,user):
        self.user = user
                

def dump_to_static_folderfile(filename_for_static_folder, data):
    """Serialize the given data and write it to a file at the given path."""
    from django.conf import settings
    
    command_dir = os.path.abspath(settings.PROJECT_ROOT)
    static_folder = os.path.join(command_dir, "media", "static")
    path = os.path.join(static_folder, filename_for_static_folder)
    log.debug ("dumping to: %s" % path)
    file = open(path, 'w')
    file.write(data)
    file.close()
    
def decode_to_unicode_html(html_string):
    converted = UnicodeDammit(html_string, isHTML=True)
    if not converted.unicode:
        # print converted.originalEncoding
        raise UnicodeDecodeError(
         "Failed to detect encoding, tried [%s]",
         ', '.join(converted.triedEncodings))
    return converted.unicode

def smart_unicode_encode( s ):
    for encode in [
    "utf8",
    "gb18030",
    "latin1",
    "ascii"
    ]:
        try:
            t = encoding.smart_unicode( s, encode )
            return t
        except:
            pass
    return u""


