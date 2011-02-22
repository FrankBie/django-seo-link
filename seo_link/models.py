import logging as log

from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q

from django.utils.translation import  ugettext_lazy as _
import re

class MatchType(models.Model):
    """
    Class Represents the Match Types
    StartsWith
    ExactMatch
    Regex
    """
    name = models.CharField(editable=True, blank=False, max_length=255)
    
    class Meta:
        verbose_name = _('Match Type')
        verbose_name_plural = _('Match Types')
    
    def __unicode__(self):
        return self.name

class ExcludePathManager(models.Manager):
    
    def get_global_exclude_pathes(self):
        rs = ExcludePath.objects.filter(is_global=True).all()
        return rs
        
        
class ExcludePath(models.Model):
    MATCHTYPE_STARTSWITH = 1
    MATCHTYPE_EXACT = 2
    MATCHTYPE_REGEX = 3
    
    type = models.ForeignKey(MatchType)
    name = models.CharField(editable=True, blank=False, max_length=255)
    pattern = models.CharField(editable=True, blank=False, max_length=255)
        
    objects = ExcludePathManager()
    
    class Meta:
        unique_together = ('type', 'pattern')
        verbose_name = _('Exclude Path')
        verbose_name_plural = _('Exclude Pathes')
    
    def __unicode__(self):
        return self.name

    def is_matching(self, to_test_path):
        match = False
        to_test_path_len = len(to_test_path)
        
        if self.type.id == self.MATCHTYPE_STARTSWITH and unicode(to_test_path).find(self.pattern) == 0:
            match = True
        elif self.type.id == self.MATCHTYPE_EXACT and unicode(to_test_path).find(self.pattern) == 0 and (to_test_path_len == len(self.pattern)):
            match = True
        elif self.type.id == self.MATCHTYPE_REGEX: 
            try:
                #@TODO: MAKE REGEX WORKING HERE
                #@TODO; need to cache the regex?
                reg_ex = re.match(self.pattern.strip().rstrip(),to_test_path)
                raise Exception("reg ex not implemented")
            except Exception,e:
                log.error(e)
                log.error("regular expression broken %s" % self.pattern)
            
        return match
    
    

class ReplacementTemplate(models.Model):
    """
    Class representing the terms that should be relaced by a template
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
            self.path = self.words.strip().rstrip()
        super(TargetPath, self).save(**kwargs)
        
        
class TermManager(models.Manager):
    """
    Manager for the Terms
    """
    def get_relevant_terms(self, to_test_path, min_word_count=0):
        """
        Method to get Terms telated to the path, remove ignore pattern matching terms
        """
        
        # get all none global ignore pathes
        excludepath_none_global_ids = set(
                                          ExcludePath.objects.all().values_list('id', flat=True)
        )
        exclude_pathes_none_global = ExcludePath.objects.filter(id__in=excludepath_none_global_ids)
        # all terms without a ignore pattern
        no_restricted_terms_ids = set(
                                      Term.objects.filter(
                                        Q(is_active=True) and 
                                        Q(ignore_pattern__isnull=True)
                                    ).values_list('id', flat=True)
        )
        relevant_term_ids = no_restricted_terms_ids
        # now get the ones that have a restriction but the restriction does not apply
        #terms_without_restriction = Term.objects.filter(id__in=no_restricted_terms_ids)
        #print "none restricted terms %s" % terms_without_restriction
        
        not_matching_ignore_pathes_ids = []
        #@fixme: Expensive here, cheaper solution?
        for ignore_path in exclude_pathes_none_global:
            if not ignore_path.is_matching(to_test_path):
                not_matching_ignore_pathes_ids.append(ignore_path.id)
        
        terms_ids_not_matchin_ignore_pathes = Term.objects.filter(
                                                Q(ignore_pattern__id__in=not_matching_ignore_pathes_ids)
        ).values_list('id', flat=True)
        # get the terms that have not matched to any ignore path
        relevant_term_ids = relevant_term_ids.union(terms_ids_not_matchin_ignore_pathes)
        relevant_terms = Term.objects.all().filter(
                                                   Q(id__in=relevant_term_ids) 
                                                   and Q(word_count__gte=min_word_count)
        ).order_by("-word_count")
        return relevant_terms


class Term(models.Model):
    """
    Class representing the terms that should be replaced by a template
    """
    words = models.CharField(editable=True, blank=False, max_length=255)
    word_count = models.PositiveIntegerField(editable=False, blank=False, default=0)
    replacement_template = models.ForeignKey(ReplacementTemplate)
    target_path = models.ForeignKey(TargetPath, null=True, blank=True)
    ignore_pattern = models.ManyToManyField(ExcludePath, blank=True,)
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


class CacheKeyManager(models.Manager):
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