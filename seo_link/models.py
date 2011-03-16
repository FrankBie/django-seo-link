# -*- coding: utf-8 -*-
import re
import logging as log

from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.utils.translation import  ugettext_lazy as _
from django.utils.datetime_safe import datetime



class MatchType(models.Model):
    """
    Class Represents the Match Types
    StartsWith
    ExactMatch
    Regex
    Contains
    """
    name = models.CharField(editable=True, blank=False, max_length=255)
    
    class Meta:
        verbose_name = _('Match Type')
        verbose_name_plural = _('Match Types')
    
    def __unicode__(self):
        return self.name


class OperatingPathManager(models.Manager):
    
    def get_global_exclude_pathes(self):
        rs = OperatingPath.objects.filter(is_global=True).all()
        return rs
        
        
class OperatingPath(models.Model):
    MATCHTYPE_STARTSWITH = 1L
    MATCHTYPE_EXACT = 2L
    MATCHTYPE_REGEX = 3L
    MATCHTYPE_CONTAINS = 4L
    
    type = models.ForeignKey(MatchType)
    name = models.CharField(editable=True, blank=False, max_length=255)
    pattern = models.CharField(editable=True, blank=False, max_length=255)
    is_include = models.BooleanField(editable=True, blank=False, default=False)
    
    objects = OperatingPathManager()
    
    class Meta:
        unique_together = ('type', 'pattern')
        verbose_name = _('Operating Path')
        verbose_name_plural = _('Operating Paths')
    
    def __unicode__(self):
        add=u"- "
        if self.is_include == True:
            add =u"+ "
        type_str = u""
        if self.type.id == self.MATCHTYPE_STARTSWITH:
            type_str = u"Starts:  "
        elif self.type.id == self.MATCHTYPE_EXACT:
            type_str = u"Exact:   "
        elif self.type.id == self.MATCHTYPE_REGEX: 
            type_str = u"RegEx:   "
        elif self.type.id == self.MATCHTYPE_CONTAINS: 
            type_str = u"Contains:"
        
        return add + type_str +  self.name

    def is_matching(self, to_test_path):
        match = False
        to_test_path_len = len(to_test_path)
        clean_pattern =self.pattern.strip()
        if self.type.id == self.MATCHTYPE_STARTSWITH and to_test_path.find(clean_pattern) == 0:
            match = True
        elif self.type.id == self.MATCHTYPE_EXACT and to_test_path.find(clean_pattern) == 0 and (to_test_path_len == len(clean_pattern)):
            match = True
        elif self.type.id == self.MATCHTYPE_REGEX: 
            try:
                reg_ex = re.match(self.pattern.strip(), to_test_path)
                if reg_ex is not None:
                    match = True
                    
            except re.error, e:
                log.error(e)
                log.error("regular expression broken %s" % clean_pattern)
        
        elif self.type.id == self.MATCHTYPE_CONTAINS and to_test_path.find(clean_pattern) != -1:
            match = True
            
        return match
    

class ReplacementTemplate(models.Model):
    """
    Class representing the Templates terms that should be replaced by a template
    """
    name = models.CharField(editable=True, blank=False, max_length=255)
    template_filename = models.CharField(editable=True, blank=False, max_length=255)
    
    class Meta:
        verbose_name = _('Replacement Template')
        verbose_name_plural = _('Replacement Templates')
    
    def __unicode__(self):
        return self.name


class TargetPath(models.Model):
    """ Target Path for the term """
    
    name = models.CharField(editable=True, blank=False, max_length=255)
    path = models.CharField(editable=True, blank=False, max_length=1024)
    is_external = models.BooleanField(editable=True, default=False)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = _('Target Path')
        verbose_name_plural = _('Target Paths')
        
    
    def save(self, **kwargs):
        """
        Automatically set the word count on save/update
        """
        if len(self.path) > 0:
            self.path = self.path.strip().rstrip()
        super(TargetPath, self).save(**kwargs)
        
        
class TermManager(models.Manager):
    """
    Manager for the Terms
    """
    def get_relevant_terms(self, to_test_path, min_word_count=0):
        """
        Method to get Terms related to the path, remove ignore pattern matching terms
        add include matching terms
        """
        matching_include_path_ids = []
        matching_exclude_path_ids = []
        op_pathes_include = []
        op_pathes_exclude = []
        # all terms without a pattern
        no_restricted_terms_ids =Term.objects.filter(is_active=True).filter(operating_path__isnull=True).values_list('id', flat=True)
        relevant_term_ids = [x for x in no_restricted_terms_ids]
        
        # get all exclude pathes
        op_path_exclude_ids = OperatingPath.objects.filter(is_include=False).values_list('id', flat=True)
        # includes
        op_path_include_ids = OperatingPath.objects.filter(is_include=True).values_list('id', flat=True)
        if op_path_include_ids:
            op_pathes_include = OperatingPath.objects.filter(id__in=op_path_include_ids)
        if op_path_exclude_ids:
            op_pathes_exclude = OperatingPath.objects.filter(id__in=op_path_exclude_ids)
        
        # test exclude pathes
        for exclude_path in op_pathes_exclude:
            if exclude_path.is_matching(to_test_path):
                if exclude_path.id not in matching_exclude_path_ids:
                    matching_exclude_path_ids.append(exclude_path.id)
        # test include pathes
        for include_path in op_pathes_include:
            if include_path.is_matching(to_test_path):
                if include_path.id not in matching_include_path_ids:
                    matching_include_path_ids.append(include_path.id)
            
        # now mix the buckets
        to_include_term_ids =  Term.objects.filter(is_active=True).filter(operating_path__id__in=matching_include_path_ids).values_list('id', flat=True)
        #log.warn("include term ids %s"%(to_include_term_ids) )
        to_exclude_term_ids = Term.objects.filter(is_active=True).filter(operating_path__id__in=matching_exclude_path_ids).values_list('id', flat=True)
        # buckets with term ids are filled
        # now get the term obj to the ids
        positive_term_ids = [x for x in relevant_term_ids]
        positive_term_ids += [x for x in to_include_term_ids]
        final_set = []
        for x in positive_term_ids:
            if x not in to_exclude_term_ids:
                if x not in final_set:
                    final_set.append(x)
                    
        relevant_terms = Term.objects.filter(word_count__gte = min_word_count).filter(id__in = final_set).exclude(is_active = False)  
        relevant_terms = relevant_terms.order_by("-word_count") 
        
        # need to be ordered by wordcount longest first
        return relevant_terms


class Term(models.Model):
    """
    Class representing the terms that should be replaced by a template
    """
    words = models.CharField(editable=True, blank=False, max_length=255)
    word_count = models.PositiveIntegerField(editable=False, blank=False, default=0)
    replacement_template = models.ForeignKey(ReplacementTemplate)
    target_path = models.ForeignKey(TargetPath, null=True, blank=True)
    operating_path = models.ManyToManyField(OperatingPath, blank=True)
    is_case_sensitive = models.BooleanField(editable=True, default=False)
    is_active = models.BooleanField(editable=True, default=False)
        
    objects = TermManager()
    
    class Meta:
        verbose_name = _('Term')
        verbose_name_plural = _('Terms')
        unique_together = ('words', 'word_count')

    
    def save(self, **kwargs):
        """
        Automatically set the word count on save/update
        """
        if len(self.words) > 0:
            self.words = self.words.strip().rstrip()
        self.word_count = self._calculate_word_count()
        super(Term, self).save(**kwargs)

    def _calculate_word_count(self):
        return len(self.words.split(None))

    def __unicode__(self):
        return u''.join(self.words)


# Admin Testing Model
class TestUrl(models.Model):
    test_url = models.CharField(editable=True, blank=False, max_length=1024)
    created_at = models.DateTimeField(editable=False, blank=False)
    tested_at = models.DateTimeField(editable=False, blank=True, null=True)
    
    class Meta:
        verbose_name = _('TestUrl')
        verbose_name_plural = _('TestUrls')
        
    def save(self,**kwargs):
        """
        Automatic update the created_at date time
        """
        if not self.id:
            self.created_at = datetime.now()
        super(TestUrl, self).save(**kwargs)
        
    def __unicode__(self):
        return u"".join(self.test_url)
        
            
class TestResult(models.Model):
    page_url = models.ForeignKey(TestUrl, related_name='test_urls')
    page_title = models.CharField(blank=False, max_length=1024)
    link_url = models.CharField(blank=False, max_length=1024)
    link_text = models.CharField(blank=False, max_length=1024)
    is_injected = models.BooleanField(default=False)
    created_at = models.DateTimeField(blank=False)
    
    class Meta:
        verbose_name = _('Test Result')
        verbose_name_plural = _('Test Results')

 
class CacheKeyManager(models.Manager):
    """
    Cache Key Manager to enable multi instance caching
    """
    def get_keys(self, site_id=None, language=None):
        ret = self.none()
        if not site_id and not language:
            # Both site and language are None - return everything  
            ret = self.all()
        elif not site_id:
            ret = self.filter(language=language)
        elif not language:
            ret = self.filter(site=site_id)
        else:
            # Filter by site_id *and* by language.
            ret = self.filter(site=site_id).filter(language=language)
        return ret


class CacheKey(models.Model):
    '''
    This is to store a "set" of cache keys in a fashion where it's accessible 
    by multiple processes / machines.
    Multiple Django instances will then share the keys.
    This allows for selective invalidation of the menu trees (per site, per 
    language), in the cache.
    '''
    language = models.CharField(max_length=255)
    site = models.PositiveIntegerField()
    key = models.CharField(max_length=1024)
    objects = CacheKeyManager()
    
    class Meta:
        verbose_name = _('CacheKey')
        verbose_name_plural = _('CacheKeys')
        
# hack to get the signals loaded    
from seo_link.signals import *
