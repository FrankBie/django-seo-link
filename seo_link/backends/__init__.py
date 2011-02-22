import re, time
import logging as log

from django import template
from django.contrib.sites.models import  get_current_site

from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _, get_language
from django.template.context import Context

from seo_link import settings as seo_link_settings
from seo_link.models import Term 

class AbstractSeoLinkBackend(object):
    """
    This class models the general term replacement flow
    """
    
    def process_response(self, request, response):
        """
        Abstract Processing Flow
        """
        start_time = 1
        if seo_link_settings.TIMER_ON:
            start_time = time.clock()
        
        to_ignore = self._is_request_ignoreable(request, response) 
        if to_ignore:
            msg = "to ignore"
            log.debug(msg)
            return response
        # cache 
        if self._is_cached(request, response):
            msg = "check cache"
            log.debug(msg)
            resp = self._get_cached(request, response)
            return resp
        # start 
        # are there any words we need to process in this page
        # check bottom up longer terms first
        matched_term_matrix = self._get_relevant_terms_for_page(request, response)
        #msg = "matched_term_matrix: %s" % matched_term_matrix
        #log.debug(msg)
        if matched_term_matrix:
            response = self.replace_terms(request, response, matched_term_matrix)
        end_time = 0
        if seo_link_settings.TIMER_ON:
            end_time = time.clock()
        self._set_cached(request, response)
        delta = (end_time - start_time)
        
        msg = u"\n<!-- SeoLink processing time %s seconds -->\n" % (end_time - start_time)
        if delta > 1.0: 
            log.warn(msg)
        response.content = response.content + msg
        return response

    def replace_terms(self, request, response, terms):
        """ impl replace the terms here"""
        raise NotImplemented
    
    def _is_request_ignoreable(self, request, response):
        """ impl ignoring algorithm here"""
        raise NotImplemented
    
    def _get_relevant_terms_for_page(self, request, response):
        """ impl the relevance algorithm here """
        raise NotImplemented


class AbstractCachedMixin(object):
    
    def _get_lex_key(self, request):
        site = get_current_site(request)
        lang = get_language()
        key = None
        if not request.user.is_authenticated():
            #anonymous user cache key
            key = "%sreponse_%s_%s_%s" % (seo_link_settings.CACHE_KEY_PREFIX, site.id, lang, request.path)
        else:
            #authenticated user cache key
            key = "%sreponse_%s_%s__user_%s__%s" % (seo_link_settings.CACHE_KEY_PREFIX, site.id, lang, request.user.id, request.path)
        return key
    
    def _is_cached(self, request, response):
        raise NotImplemented

    def _get_cached(self, request, response):
        raise NotImplemented
    
    def _set_cached(self, request, response):
        raise NotImplemented
    
    def clear_cached(self, site_id=None, language=None, all=False):
        raise NotImplemented


class AbstractUtilsMixin(object):
    """
    Mixin containing util functions all Backends need to implement
    """
    processed_terms = []
    
    def __init__(self, *args, **kwargs):
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
                if seo_link_settings.DEBUG:
                    log.debug("count %s, term %s, term_id %s" % (times, term.words, term.id))
        return results

    def _get_global_ignore_path_list(self):
        rs = seo_link_settings.GLOBAL_EXCLUDE_PATHES
        return rs

    def _get_template_context_for_term(self, term):
        t = None
        context = Context()
        template_file = "seo_link/%s" % term.replacement_template.template_filename
        is_external_url = term.target_path.is_external
        #@fixme: target url is taken as a given, check site protocol and complete the url
        target_url = term.target_path.path
        try:
            t = template.loader.get_template(template_file)
            context = {
                'matched_term':term.words,
                'target_url':target_url
            }
            content = t.render(Context(context))
            content = content.strip().rstrip()
        except template.TemplateDoesNotExist, e:
            content = _('Template %(template)s does not exist.') % {'template': template_file}
            log.error(content)
        except Exception, e:
            content = str(e)
            log.error(content)
        context.update({
            'content': mark_safe(content),
        })
        return context

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
        """
        Select the terms that are relevant for this url
        according to their exclude path settings and
        the MIN_TERM_WORD_COUNT
        """
        current_path = request.path
        min_word_count = seo_link_settings.MIN_TERM_WORD_COUNT
        relevant_terms_path = Term.objects.get_relevant_terms(current_path, min_word_count)
        result_tuples = self._get_occuring_terms_count_page(response.content, relevant_terms_path)
        return result_tuples
    
    def _compile_regex(self, term):
        pattern = "^.*%s.*$" % (term.words.strip().rstrip())
        reg_ex = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
        if term.is_case_sensitive:
            reg_ex = re.compile(pattern, re.MULTILINE)
        return reg_ex  





