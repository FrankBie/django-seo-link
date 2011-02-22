import re
import logging as log

from django.contrib.sites.models import get_current_site
from django.core.cache import cache
from django.utils.translation import get_language
from seo_link import settings as seo_link_settings  
from seo_link.backends import AbstractCachedMixin, AbstractUtilsMixin, AbstractSeoLinkBackend
from seo_link.models import CacheKey
from BeautifulSoup import BeautifulSoup, Tag, NavigableString



class NoCachedMixin(AbstractCachedMixin):

    def _is_cached(self, request, response):
        return False

    def _get_cached(self, request, response):
        return response

    def _set_cached(self, request, response):
        pass
    
    def clear_cached(self, site_id=None, language=None, all=False):
        pass


class SimpleBackend(AbstractUtilsMixin, AbstractSeoLinkBackend, NoCachedMixin):
    """
    Simple BeutifulSoup based Backend without caching
    """
    soup = None
    iteration_count = 0
    
    def __init__(self, *args, **kwargs):
        super(SimpleBackend, self).__init__(*args, **kwargs)
                
    def replace_terms(self, request, response, terms):
        """
        Process the terms and put the templates in there
        """
        html = response.content
        pretty_html = BeautifulSoup(html).prettify()
        soup = BeautifulSoup(pretty_html)
        # sort the terms descending by wordcount manually
        # @todo: ensure that we start with the longest term first
        terms = sorted(terms, key=lambda term_pack: term_pack[0].word_count * -1)
        
        if seo_link_settings.DEBUG:
            log.debug("to_process_terms %s" % terms)
            
        for term_pack in terms:
            term, occourence = term_pack
            #print "\nprocessing term %s wc %s, occourence %s" %(term.words,term.word_count,occourence)
            # check if the text is found
            reg_ex = self._compile_regex(term)
            matched_tags = soup.findAll(text=reg_ex)
            if seo_link_settings.DEBUG:
                log.debug("matched tags count %s" % (len(matched_tags)))
            
            if matched_tags:
                new_html = None
                #@TODO: As modifiying the dom, and inserting nested templates kills
                #further processing, we need to reload the html and match it again
                # the next search term.
                #@FIXME: Limit this reloading to the max term count
                
                for cur_tag in matched_tags:
                    new_html = self._replace_nodes_get_html(soup, cur_tag, term)
                #@fixme: diry solution
                # if there is a replacement done, the new html needs to be re read
                if new_html is not None:
                    #print "pattern2 %s" % pattern
                    reg_ex = self._compile_regex(term)
                    del soup
                    soup = BeautifulSoup(new_html)
                    
                    matched_tags2 = soup.findAll(text=reg_ex)
                    #print "matched tags2 count %s" % (len(matched_tags2))
                    if len(matched_tags2) > 0:
                        new_html = None
                        for cur_tag in matched_tags2:
                            new_html = self._replace_nodes_get_html(soup, cur_tag, term)
                # if there is a replacement done, the new html needs to be re read
                if new_html is not None:
                    #print "pattern2 %s" % pattern
                    reg_ex = self._compile_regex(term)
                    del soup
                    soup = BeautifulSoup(new_html)
                    
                    matched_tags2 = soup.findAll(text=reg_ex)
                    #print "matched tags2 count %s" % (len(matched_tags2))
                    if matched_tags2:
                        new_html = None
                        for cur_tag in matched_tags2:
                            new_html = self._replace_nodes_get_html(soup, cur_tag, term)

        response.content = soup.prettify()
        if seo_link_settings.DEBUG:
            log.debug("processed_terms_count %s" % len(self.processed_terms))
            log.debug("processed_terms %s" % self.processed_terms)
            log.debug("iterations %s" % self.iteration_count)
        return response
    
    def _is_entity_found_in_parent(self, match_list, cur_tag, is_css=False, is_id=False):
        """
        function to compile the beautiful soup lookup attrs
        """
        found = False
        for entity in match_list:
            if entity:
                if is_css:
                    if not is_id:
                        # if there are multiple classes in on class definition it
                        # needs to be a regular expression
                        # {'class': re.compile(r'\bclass1\b')})
                        pattern = r'\b%s\b' % entity
                        css = { "class" : re.compile(pattern) }
                    else:
                        css = { "id" : entity }
                    found = (cur_tag.findParent(attrs=css) != None)
                else:
                    found = (cur_tag.findParent(entity) != None)
                if found:
                    break
        return found
    
    def _is_nodes_parent_tree_valid_for_replacement(self, soup2, cur_node, term):
        """
        Function to determine if the cur_node is encapsuled in any restriction
        You could restrict the replacement matching on css_id/css_class level 
        and combinations of
        These settings are used for the combinations
           OPERATIONAL_HTML_ENTITIES
           IGNORE_HTML_ENTITIES
           
           OPERATIONAL_CSS_SELECTOR_CLASSES
           OPERATIONAL_CSS_SELECTOR_IDS
           
           IGNORE_CSS_SELECTOR_CLASSES
           IGNORE_CSS_SELECTOR_IDS
           
           First it checks if OPERATIONAL_HTML_ENTITIES match with IGNORE_HTML_ENTITIES
           If any parent of the cur_node is not in the OPERATIONAL_HTML_ENTITIES List
           or in the IGNORE_HTML_ENTITIES List we do not to check further elements
           
           Any parent node of the cur_node must be either in
           OPERATIONAL_CSS_SELECTOR_CLASSES or OPERATIONAL_CSS_SELECTOR_IDS Lists Matches
           if not, no more processing need
           
           Any parent node of the cur_node is in a match of 
           IGNORE_CSS_SELECTOR_CLASSES or IGNORE_CSS_SELECTOR_IDS
           the cur_node content is not replaceable
            
           
        """
        ready_for_replace = False
        # operational html is a must
        is_operational_html = self._is_entity_found_in_parent(seo_link_settings.OPERATIONAL_HTML_ENTITIES, cur_node)
        # not in an ignore html is a must
        is_to_ignore_html = self._is_entity_found_in_parent(seo_link_settings.IGNORE_HTML_ENTITIES, cur_node)
        html_entities_parents_ok = (is_operational_html and not is_to_ignore_html)
        if not html_entities_parents_ok:
            # the entities are not ok so nothing more to check
            return False
                    
        # check operational css
        is_operational_css_class = False
        is_operational_css_ids = False
        # operate only on a selection
        if seo_link_settings.OPERATIONAL_CSS_SELECTOR_CLASSES:
            is_operational_css_class = self._is_entity_found_in_parent(seo_link_settings.OPERATIONAL_CSS_SELECTOR_CLASSES, cur_node, is_css=True)
        if seo_link_settings.OPERATIONAL_CSS_SELECTOR_IDS:
            is_operational_css_ids = self._is_entity_found_in_parent(seo_link_settings.OPERATIONAL_CSS_SELECTOR_IDS, cur_node, is_css=True, is_id=True)
        # either css class or id is in upstream parent tree
        is_operational_css = (is_operational_css_ids or is_operational_css_class)
        if not is_operational_css:
            # the operational css is not matching so we are already out
            return False
        
        is_to_ignore_css_class = False
        is_to_ignore_css_ids = False
        
        if seo_link_settings.IGNORE_CSS_SELECTOR_CLASSES:
            is_to_ignore_css_class = self._is_entity_found_in_parent(seo_link_settings.IGNORE_CSS_SELECTOR_CLASSES, cur_node, is_css=True)
        
        if seo_link_settings.IGNORE_CSS_SELECTOR_IDS:
            is_to_ignore_css_ids = self._is_entity_found_in_parent(seo_link_settings.IGNORE_CSS_SELECTOR_IDS, cur_node, is_css=True, is_id=True)
        
        is_to_ignore_css = (is_to_ignore_css_class or is_to_ignore_css_ids)
        
        # combine all
        if html_entities_parents_ok and is_operational_css and not is_to_ignore_css:
            ready_for_replace = True 
        
        return ready_for_replace
    
    def _replace_nodes_get_html(self, soup2, cur_tag, term):
        self.iteration_count += 1 
        if self._is_nodes_parent_tree_valid_for_replacement(soup2, cur_tag, term) :
            #replace the node with the template
            #and reload the soup
            new_snippet = self._get_template_context_for_term(term)
            #print "new snippet %s" % (new_snippet)
            new_html = u"" 
            #print "type cur_tag %s" % cur_tag.__class__
            if isinstance(cur_tag, NavigableString):
                if seo_link_settings.DEBUG:
                    log.debug("term %s replace: %s" % (term.words, cur_tag))
                # update the stats
                replacement_count = self.get_replacement_count_for_term(term)
                replacement_count += 1
                self.update_replacement_count_for_term(term, replacement_count)
                
                if cur_tag.parent is not None:
                    """
                    replace the text with the new nodes structure
                    """
                    parent_tag = cur_tag.parent
                    parent_tag_contents = parent_tag.contents
                    cur_tag_index = parent_tag_contents.index(cur_tag)
                    new_txt = parent_tag_contents[cur_tag_index].replace(term.words, new_snippet['content'])
                    new_node = BeautifulSoup(new_txt)
                    
                    if seo_link_settings.DEBUG:
                        log.debug("parent_tag_content %s" % parent_tag_contents)
                        log.debug("parent_tag_content [%s] : %s" % (cur_tag_index, parent_tag_contents[cur_tag_index]))
                        log.debug("new_txt %s" % (new_txt))
                        log.debug ("new_node contents %s" % new_node.contents)
                        log.debug ("new_node %s" % new_node)
                        
                    # manual replace
                    do_replace = False
                    if not seo_link_settings.REPLACE_ONLY_ONE_TIME_PER_TERM: 
                        do_replace = True
                    elif seo_link_settings.REPLACE_ONLY_ONE_TIME_PER_TERM and replacement_count < 2:
                        do_replace = True
                        
                    if do_replace:
                        if seo_link_settings.DEBUG:
                            log.debug("replacing node with %s" % new_node)

                        cur_tag.extract()
                        parent_tag.insert(cur_tag_index, new_node)
                        cur_tag = parent_tag.contents[cur_tag_index]
                
                if seo_link_settings.DEBUG:        
                    if cur_tag.parent is None:
                        log.debug("current parent is None")
            else:
                if seo_link_settings.DEBUG:
                    log.debug("matched tag class %s" % (cur_tag.__class__))

        return u"".join(soup2.prettify()) # this is dirty but it is the only way to get the modified html as a new document
    
    
class SimpleCachedBackend(SimpleBackend, AbstractCachedMixin):
    
    def __init__(self, *args, **kwargs):
        # load the stored keys.values_list('id', flat=True)
        self.cached_content = set(CacheKey.objects.values_list('key', flat=True))
        super(SimpleCachedBackend, self).__init__(*args, **kwargs) 
    
    def _is_cached(self, request, response):
        return (self._get_lex_key(request) in self.cached_content)

    def _get_cached(self, request, response):
        key = self._get_lex_key(request)
        cached_content = cache.get(key, None)
        if cached_content:
            return cached_content
        return None

    def _set_cached(self, request, response):
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
    

