# -*- coding: UTF-8 -*-
import re
import logging as log

from django.contrib.sites.models import get_current_site
from django.core.cache import cache
from django.utils.translation import get_language

from lxml import etree
import lxml.html
import lxml.html.soupparser
from lxml.html import HtmlElement
from lxml.etree import LxmlError, HTMLParser, tostring
from lxml.html.clean import clean_html

from BeautifulSoup import BeautifulSoup

from seo_link import settings as seo_link_settings  
from seo_link.backends import AbstractCachedMixin, AbstractUtilsMixin, AbstractSeoLinkBackend, \
    OperationalCacheMixin
from seo_link.backends.simple import NoCachedMixin
from seo_link.models import CacheKey



class LXMLBackend(AbstractUtilsMixin, NoCachedMixin,AbstractSeoLinkBackend):
    """
    Simple Lxml based Backend without caching
    """
    soup = None
    iteration_count = 0
    
    def __init__(self, *args, **kwargs):
        super(LXMLBackend, self).__init__(*args, **kwargs)
                
    def replace_terms(self, request, response, terms):
        """
        Process the terms and put the templates in there
        """
        
        html_uni = None
        if len(response._container) == 1:
            # we want to take the unicode version of the content
            html_uni = response._container[0] 
        else:
            html_uni = unicode(response.content)# 
        html = html_uni
            
        if seo_link_settings.LXML_BEAUTIFULSOUP_PRETTIFY:
            html = BeautifulSoup(html_uni).renderContents(encoding="utf-8")
        
        if seo_link_settings.LXML_CLEANER_ON:
            html = clean_html(html_uni)
            
        # ensure that we start with the longest term first
        terms = sorted(terms, key=lambda term_pack: term_pack[0].word_count * -1)
        
        max_occourence = 0
        for term_pack in terms:
            term, occourence = term_pack
            if max_occourence < occourence:
                max_occourence = occourence
        run = 0    
        for term_pack in terms:
            term, occourence = term_pack
            # find the terms in the document
            html = self._get_replaced_html(html, term)
            run = run + 1
 
        response.content = html
#        if seo_link_settings.DEBUG:
#            log.debug("processed_terms_count %s" % len(self.processed_terms))
#            log.debug("processed_terms %s" % self.processed_terms)
#            log.debug("iterations %s" % self.iteration_count)
        return response     
    
    def _get_replaced_html(self, html, term):
        """
        replace all occourences for a term.words in the html, but 
        find the nodes using lxml
        and process the replacement in txt to subtree and replace new_subtree with
        matched node
        """
        html_doc_tree = lxml.html.fromstring(html)
        matched_tags = self._find_elements_for_term(html_doc_tree, term)
        #log.warn("matched tags count %s" % (len(matched_tags)))
        if len(matched_tags) > 0:    
            html = None
            for element in matched_tags:
                html = self._replace_nodes_get_html(html_doc_tree, element, term)
        out = lxml.html.tostring(html_doc_tree)
        return out
    
    def _find_elements_for_term(self, html_doc_tree, term):
        """
        Function walks the tree over all elements
        and checks if in element.text or element.tail is a match for the term
        """
        matched_tags = []
        reg_ex = self._compile_regex(term)
        walk_all = html_doc_tree.getiterator()
        walk_subset = []
        for element in walk_all:
            if element.tag in seo_link_settings.OPERATIONAL_HTML_ENTITIES:
                walk_subset += element
        for element in walk_subset:
                # walks the stuff down so we could start with the 
                #is the term in the text?
                has_children = (len(element.getchildren()) > 0)
                found_txt = False
                if element.text is not None and element.text != "\n" :
                    #reg_ex = self._compile_regex()
                    txt = element.text
                    found_txt = (reg_ex.search(txt) != None)
                    found_pos = txt.find(term.words)
                    if (found_txt):
                        if isinstance(element, HtmlElement) and (element not in matched_tags): 
                            matched_tags.append(element)
                # a matching text is found in tail                            
                if element.tail is not None and element.tail != "\n" :
                    txt = element.tail
                    found_tail = (reg_ex.search(txt) != None)
                    if (found_tail):
                        # extra handling, redundancy, put the element and the parent 
                        # to the matched tags
                        parent = element.getparent()
                        if isinstance(parent, HtmlElement) and (parent not in matched_tags): 
                            matched_tags.append(parent)
                        if isinstance(element, HtmlElement) and (element not in matched_tags): 
                            matched_tags.append(element)
                
        #log.warn("term: %s found: %s" % (term.words, len(matched_tags)))
        return matched_tags
    
    def _is_nodes_parent_tree_valid_for_replacement(self, tree, cur_node, term):
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
        #need to check if the term is really ready
        return ready_for_replace
    
    def _replace_nodes_get_html(self, root_doc, cur_element, term):
        """
        replace the nodes if they are valid for replacement
        work on the html to do that
        """
        
        self.iteration_count += 1 
        # if the tail contains the term the stuff gets removed?
        if self._is_nodes_parent_tree_valid_for_replacement(root_doc, cur_element, term) :
            #replace the node with the template
            new_snippet_html = self._get_template_context_for_term(term)
            #    log.debug("term %s replace: %s" % (term.words, cur_element))
            parent_element = cur_element.getparent()
            if parent_element is not None:
                # chek somehow if this is replace allowed textwise
                cur_element_html = lxml.html.tostring(cur_element, pretty_print=True)
                #updated_element_html=cur_element_html.replace(term.words, new_snippet_html['content'],1)
                updated_element_html = self.save_tag_replace(cur_element_html, term, new_snippet_html['content'])
                try:
                    updated_element_subtree = lxml.html.fragment_fromstring(updated_element_html, create_parent=False)
                    parent_element.replace(cur_element, updated_element_subtree)
                except LxmlError, e:
                    #log.warn(e)
                    pass
        return u"".join(lxml.html.tostring(root_doc)) 
    
    def save_tag_replace(self, in_txt, term, replace_with):
        """
        Replace the needle with replace_with, 
        only if it is not nested in IGNORE_HTML_ENTITIES 
        """
        # make sure that the term is not encapsuled in any none processing tag stringwise
        needle = term.words
        needle_occourence = in_txt.split(needle)
        prior_tag_name = None
        save_to_replace = False
        out = ""
        last_match_pos = len(in_txt)
        if needle_occourence:
            needle_occourence = len(needle_occourence) - 1
        else:
            # no needle - nothing to do
            return in_txt
        # replace not only one occourence of the string
        last_run_end_pos = len(in_txt)
        for x in range(needle_occourence):
            #multiple occurences?
            save_to_replace = False
            prior_tag_start_pos = -1
            prior_tag_open_str = None
            prior_tag_name = None
            last_match_pos = in_txt.rfind(needle, 0, last_run_end_pos)
            last_run_end_pos = last_match_pos 
            # is there a needle in the string?
            if last_match_pos != -1:
                tmp_str = in_txt[0:last_match_pos]
                prior_tag_start_pos = tmp_str.rfind("<")
                # try to get the tagname that is before the found position
                if prior_tag_start_pos != -1:
                    tmp_str = in_txt[prior_tag_start_pos + 1:last_match_pos]
                    prior_tag_end_pos = tmp_str.rfind(">")
                    if prior_tag_end_pos != -1: 
                        prior_tag_open_str = tmp_str[0:prior_tag_end_pos]
                else:
                    # no prior tag
                    save_to_replace = True
            # no needle found
            else:
                save_to_replace = False
            
            # found a tag before the needle
            if prior_tag_open_str:
                prior_tag_names = None
                prior_tag_name = None
                # extract the tag name
                if prior_tag_open_str.strip().rfind(" ") != -1:
                    prior_tag_names_list = prior_tag_open_str.split(" ")
                    prior_tag_name = prior_tag_names_list[0].strip()
                    #log.warn("prior_tag_name: %s" % prior_tag_names)
                else:
                    prior_tag_names_str = prior_tag_open_str.strip() 
                    #log.warn("prior_tag_name: %s" % prior_tag_names_str)
                    if prior_tag_names_str.rfind(" ") != -1:
                        prior_tag_names_list = prior_tag_names_str.split(" ")
                        prior_tag_name = prior_tag_names_list[0].strip()
                    else:
                        prior_tag_name = prior_tag_names_str.strip()
            # check if the prior tag name is in the ignore settings
            if prior_tag_name is not None and prior_tag_name.lower() not in seo_link_settings.IGNORE_HTML_ENTITIES:
                save_to_replace = True
            
            if save_to_replace:
                # handle the replacement counting
                replacement_count = self.get_replacement_count_for_term(term)
                replacement_count += 1
                self.update_replacement_count_for_term(term, replacement_count)
                do_replace = False
                if not seo_link_settings.REPLACE_ONLY_ONE_TIME_PER_TERM: 
                    do_replace = True
                elif seo_link_settings.REPLACE_ONLY_ONE_TIME_PER_TERM and replacement_count < 2:
                    do_replace = True
                # do the replacement
                if do_replace:
                    #manual replace one occourence
                    head = in_txt[:last_match_pos]
                    tail = in_txt[last_match_pos + len(needle):]
                    out = head + replace_with + tail
                else:
                    out = in_txt
            else:
                    out = in_txt
            # save the new in_txt for the next run
            in_txt = out        
        return out              
    
    def _is_entity_found_in_parent(self, match_list, cur_tag, is_css=False, is_id=False):
        """
        function to compile the beautiful soup lookup attrs
        checks the upper tree if one of the elements in the match_list is present
        if is_css == True -> looks for class
        if is_id == True -> looks for id
        if is_css == False and is_id == False looks for html entities
        """
        found = False
        for entity in match_list:
            if entity:
                if is_css:
                    if is_id:
                        found = self._is_in_uppertree_id_entity(entity, cur_tag)
                    else:
                        found = self._is_in_uppertree_css_class_entity(entity, cur_tag)
                else:
                    found = self._is_in_uppertree_html_entity(entity, cur_tag)
                if found:
                    break
        return found

    def _is_in_uppertree_css_class_entity(self, css_class_name, element):
        found = False
        pattern = r'\b%s\b' % css_class_name
        reg_ex = re.compile(pattern)
        # is a class attribute there?
        if "class" in element.attrib.keys():
            found = (reg_ex.match(element.attrib['class']) != None)
        
        if not found: 
            walk_up = element.iterancestors()
            for x in walk_up:
                if "class" in x.attrib.keys():
                    found = (reg_ex.match(x.attrib['class']) != None)
                if found:
                    #log.warn("classmatch: %s" % (x.attrib['class']))
                    break
                
        if found is None:
            found = False
        return found

    def _is_in_uppertree_id_entity(self, css_id, element):
        found = False
        if "id" in element.attrib.keys():
            val = element.attrib['id']
            if val:
                found = (val.strip().find(css_id) == 0)
        if not found: 
            walk_up = element.iterancestors()
            for x in walk_up:
                if "id" in x.attrib.keys():
                    val = x.attrib['id']
                    if val:
                        found = (val.strip().find(css_id) == 0)
                if found:
                    break
        if found is None:
            found = False
        return found
    
    def _is_in_uppertree_html_entity(self, html_entity_type_name, element):
        found = False
        if isinstance(element, HtmlElement) == False:
            return found
        found = (element.tag == html_entity_type_name.lower())
        if not found: 
            walk_up = element.iterancestors()
            for x in walk_up:
                found = (x.tag == html_entity_type_name.lower()) 
                if found:
                    break
                if x == element.body:
                    break
        if found is None:
            found = False
        return found
    
    
class LXMLCachedBackend(OperationalCacheMixin,LXMLBackend):
    
    def __init__(self, *args, **kwargs):
        # load the stored keys.values_list('id', flat=True)
        super(LXMLCachedBackend, self).__init__(*args, **kwargs) 
