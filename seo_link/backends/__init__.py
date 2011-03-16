# -*- coding: utf-8 -*-
import re, time
import logging as log

from django import template
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.contrib.sites.models import  get_current_site

from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _, get_language
from django.template.context import Context
from django.template.defaultfilters import safe

from seo_link import settings as seo_link_settings
from seo_link.models import Term , CacheKey



# cache vars
CACHE_RELATED_TERMS_PER_PAGE = {}
CACHE_TERM_TEMPLATES = {} 

class AbstractSeoLinkBackend(object):
    """
    This class models the general term replacement flow
    """
    def process_response(self, request, response):
        """
        Abstract Processing Flow
        check if it is processable
        lookup the cache
        process
        put to cache
        """
        # check if the NO_PROCESSING_GET_PARAM setting is set
        try:
            if request.method == "GET" and request.GET.get(seo_link_settings.NO_PROCESSING_GET_PARAM, None):
                return response
        except Exception, e:
            log.warn(e)
        
        start_time = 1
        if seo_link_settings.TIMER_ON:
            start_time = time.clock()
        
        to_ignore = self._is_request_ignoreable(request, response) 
        if to_ignore:
            msg = "to ignore"
            log.debug(msg)
            return response
        # check cache 
        if self._is_cached(request, response):
            msg = "check cache"
            log.debug(msg)
            resp = self._get_cached(request, response)
            if seo_link_settings.TIMER_ON:
                end_time = time.clock()
                delta = (end_time - start_time)
                msg = u"\n<!-- SeoLink cached processing time %s seconds -->\n</body>" % (end_time - start_time)
                if delta > 1.0: 
                    log.warn(msg)
                resp.content = resp.content.replace("</body>", msg)
            return resp
        # start 
        # are there any words we need to process in this page
        # check bottom up longer terms first
        matched_term_matrix = self._get_relevant_terms_for_page(request, response)
        if matched_term_matrix:
            response = self.replace_terms(request, response, matched_term_matrix)
        end_time = 0
        # put the result to the cache
        self._set_cached(request, response)
        
        if seo_link_settings.TIMER_ON:
            end_time = time.clock()
            delta = (end_time - start_time)
            msg = u"\n<!-- SeoLink processing time %s seconds -->\n</body>" % (end_time - start_time)
            if delta > 1.0: 
                log.warn(msg)
            response.content = response.content.replace("</body>", msg)
        return response

    def replace_terms(self, request, response, terms):
        raise ImproperlyConfigured
    
    def _is_request_ignoreable(self, request, response):
        to_test_path = request.path
        ignore = False
        global_ignore_pathes = seo_link_settings.GLOBAL_EXCLUDE_PATHES
        for ignore_path in global_ignore_pathes:
            ignore = (unicode(to_test_path).find(ignore_path) == 0) 
            if ignore:
                break
        return ignore
    
    def _get_relevant_terms_for_page(self, request, response):
        raise ImproperlyConfigured
    

class AbstractCachedMixin(object):
    
    def _get_lex_key(self, request):
        """
        Generate the caching key for cached backends
        """
        site = get_current_site(request)
        lang = get_language()
        key = None
        full_path = request.get_full_path()
        if not request.user.is_authenticated():
            #anonymous user cache key
            key = "%sre_%s_%s_%s" % (seo_link_settings.CACHE_KEY_PREFIX, site.id, lang, full_path)
        else:
            #authenticated user cache key
            key = "%sre_%s_%s__user_%s__%s" % (seo_link_settings.CACHE_KEY_PREFIX, site.id, lang, request.user.id, full_path)
        if len(key) > 1024:
            raise ImproperlyConfigured("Cache key max size is 1024: %s", key)
        
        return key
    
    def _is_cached(self, request, response):
        raise ImproperlyConfigured

    def _get_cached(self, request, response):
        raise ImproperlyConfigured
    
    def _set_cached(self, request, response):
        raise ImproperlyConfigured
    
    def clear_cached(self, site_id=None, language=None, all=False):
        raise ImproperlyConfigured


class AbstractUtilsMixin(object):
    """
    Mixin containing util functions all Backends need to implement
    """
    processed_terms = []
    
    def __init__(self, *args, **kwargs):
        self._cache_related_terms_per_page = CACHE_RELATED_TERMS_PER_PAGE
        self._cache_term_templates = CACHE_TERM_TEMPLATES
        super(AbstractUtilsMixin, self).__init__(*args, **kwargs)

    def get_replacement_count_for_term(self, term):
        """
        internal counting of the operated replacements
        """
        count = 0
        for x in self.processed_terms:
            if x[0] == term:
                count = x[1]
        return count

    def update_replacement_count_for_term(self, term, new_count):
        for x in self.processed_terms:
            if x[0] == term:
                self.processed_terms.remove(x)
        self.processed_terms.append((term, new_count))
    
    def _get_occuring_terms_count_page(self, html, terms):
        """
        this function checks via text search how often
        the term is in the page and applies 
        seo_link_settings.MAX_DIFFERENT_TERM_REPLACMENT_PER_PAGE
        """
        
        # start with the longest terms first
        results = []
        for term in terms:
            times = html.count(term.words)
            html = html.replace(term.words, '')
            if times > 0:
                if seo_link_settings.MAX_DIFFERENT_TERM_REPLACMENT_PER_PAGE is not None:
                    if len(results) < seo_link_settings.MAX_DIFFERENT_TERM_REPLACMENT_PER_PAGE:
                        results.append((term, times))
                else:
                    results.append((term, times))
#                if seo_link_settings.DEBUG:
#                    log.debug("count %s, term %s, term_id %s" % (times, term.words, term.id))
        return results

    def _get_global_ignore_path_list(self):
        rs = seo_link_settings.GLOBAL_EXCLUDE_PATHES
        return rs

    def _get_template_context_for_term(self, term):
        #@todo: make a preloading of term templates to prevent io
        t = None
        content = None
        context = Context()
        template_file = "seo_link/%s" % term.replacement_template.template_filename
        is_external_url = term.target_path.is_external
        target_url = term.target_path.path
        key_tuple = (term.id, template_file, target_url)
        # get it from the local cache
        error = False
        if key_tuple in self._cache_term_templates.keys():
            content = self._cache_term_templates[key_tuple]
        if content is None:
            try:
                t = template.loader.get_template(template_file)
                context = {
                    'matched_term':term.words,
                    'target_url':target_url
                }
                content = t.render(Context(context))
                content = content.strip().rstrip()
                content = content.replace("\n", " ")
            except template.TemplateDoesNotExist, e:
                content = _('Template %(template)s does not exist.') % {'template': template_file}
                log.error(content)
                error = True
            except Exception, e:
                content = unicode(e)
                log.error(content)
                error = True
            # update cache
            if key_tuple not in self._cache_term_templates.keys() and not error:
                self._cache_term_templates[key_tuple] = content 
        
        context.update({
            'content': safe(content),
        })
        return context

    def _get_relevant_terms_for_page(self, request, response):
        """
        Select the terms that are relevant for this url
        according to their exclude path settings and
        the MIN_TERM_WORD_COUNT
        """
        current_path = request.path
        
        if (current_path in self._cache_related_terms_per_page.keys()):
            if seo_link_settings.DEBUG:
                log.debug("get from cache containes now %s elements" %(len(self._cache_related_terms_per_page)))
            return self._cache_related_terms_per_page[current_path]
        
        min_word_count = seo_link_settings.MIN_TERM_WORD_COUNT
        relevant_terms_path = Term.objects.get_relevant_terms(current_path, min_word_count)
        result_tuples = self._get_occuring_terms_count_page(response.content, relevant_terms_path)
        
        if (current_path not in self._cache_related_terms_per_page.keys()):
        #    # update the cache
            self._cache_related_terms_per_page[current_path] = result_tuples
            if seo_link_settings.DEBUG:
                log.warn("cache updated containes now %s elements" %(len(self._cache_related_terms_per_page)))
        return result_tuples
    
    def _compile_regex(self, term):
        pattern = "^.*%s.*$" % (term.words.strip().rstrip())
        reg_ex = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
        if term.is_case_sensitive:
            reg_ex = re.compile(pattern, re.MULTILINE)
        return reg_ex  
    
    def clear_related_terms_per_page_cache(self):
        """
        Function to delete the page term cache and the template term cache
        """
        #@todo: make it multi instance capable
        elem_count = len(self._cache_related_terms_per_page)
        if elem_count > 0:
            #log.warn("cache elements before clear %s" % self._cache_related_terms_per_page)
            del self._cache_related_terms_per_page    
            self._cache_related_terms_per_page = {}
            #log.warn("dropped related_terms_per_page_cache, contained %s elements" %(elem_count))
        if len(self._cache_term_templates) > 0:
            del self._cache_term_templates
            self._cache_term_templates = {}


class OperationalCacheMixin(AbstractCachedMixin):
    """
    Marker class for valid clear calls from the signals
    """
    def __init__(self, *args, **kwargs):
        # load the stored keys.values_list('id', flat=True)
        self.cached_content = set(CacheKey.objects.values_list('key', flat=True))
        super(OperationalCacheMixin, self).__init__(*args, **kwargs) 
    
    def _is_cached(self, request, response):
        # cache only gets
        log.debug("op is cached %s" %(self))
        if not request.method == "GET":
            return False
        return (self._get_lex_key(request) in self.cached_content)

    def _get_cached(self, request, response):
        key = self._get_lex_key(request)
        cached_content = cache.get(key, None)
        if cached_content:
            return cached_content
        return None

    def _set_cached(self, request, response):
        # operate only on get
        if not request.method == "GET":
            return None 
        key = self._get_lex_key(request)
        duration = seo_link_settings.CACHE_DURATION
        lang = get_language()
        site = get_current_site(request)
        if (key in self.cached_content):
            #remove if exists from cache
            self.cached_content.remove(key)
            #CacheKey.objects.delete(key=key, language=lang, site=site.id)
        else:
            #set cache
            cache.set(key, response, duration)
            if key not in self.cached_content:
                self.cached_content.add(key)
        # We need to have a list of the cache keys for languages and sites that
        # span several processes - so we follow the Django way and share through 
        # the database. It's still cheaper than recomputing every time!
        # This way we can selectively invalidate per-site and per-language, 
        # since the cache shared but the keys aren't 
        CacheKey.objects.get_or_create(key=key, language=lang, site=site.id)
    
    def clear_cached(self, site_id=None, language=None, all=False):
        '''
        This invalidates the cache for a content (site_id and language)
        '''
        if all:
            cache_keys = CacheKey.objects.get_keys()
        else:
            cache_keys = CacheKey.objects.get_keys(site_id, language)        
        to_be_deleted = [obj.key for obj in cache_keys]
        cache.delete_many(to_be_deleted)
        cache_keys.delete()
        # reload cached keys
        self.cached_content = set(CacheKey.objects.values_list('key', flat=True))

