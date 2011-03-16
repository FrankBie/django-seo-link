# -*- coding: utf-8 -*-
import re
import logging as log

from django import forms
from django.conf import settings as django_settings 
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.datetime_safe import datetime

from BeautifulSoup import BeautifulSoup, Tag


from seo_link.models import Term, OperatingPath, TestUrl, TestResult
from seo_link.models import TargetPath, ReplacementTemplate, MatchType 
    
from seo_link.utils import removeNL, DummyClient, dump_to_static_folderfile
from seo_link.settings import NO_PROCESSING_GET_PARAM, DUMP_TEST_URLS_FAILURES_TO_STATIC


class OperatingPathAdminForm(forms.ModelForm):
    
    class Meta:
        model = OperatingPath
    
    def __init__(self, *args, **kwds):
        super(OperatingPathAdminForm, self).__init__(*args, **kwds)
    
    def clean_pattern(self):
        # @todo: related to the type check if the pattern is valid
        # starts with = beginning with /
        # exact same
        # regex # regex is compileable
        
        #pattern = "^.*%s.*$" % (term.words.strip().rstrip())
        self.cleaned_data["pattern"] = self.cleaned_data["pattern"].strip()
        if self.cleaned_data["type"] == OperatingPath.MATCHTYPE_REGEX:
            try:
                reg_ex = re.compile(self.cleaned_data["pattern"])
            except re.error, e:
                raise ValidationError(e)
        
        return self.cleaned_data["pattern"]
    

class OperatingPathAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_include', 'type', 'pattern',)
    #inlines = [ MatchTypeInline ]
    form = OperatingPathAdminForm


class ReplacementTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'template_filename',)


class TargetPathAdminForm(forms.ModelForm):

    class Meta:
        model = TargetPath
    
    def clean_path(self):
        ext = False
        try:
            ext = self.cleaned_data["is_external"]
        except KeyError, e:
            pass
        if self.cleaned_data["path"] is not None and ext == False:
            if (self.cleaned_data["path"].find("/") != 0):
                raise ValidationError("internal path have to start with /")
        return self.cleaned_data["path"]


class TargetPathAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_external', 'path')
    form = TargetPathAdminForm


class TermAdmin(admin.ModelAdmin):
    list_display = ('words', 'word_count', 'target_path', 'replacement_template', 'is_active')
   

class TestUrlAdminForm(forms.ModelForm):
    
    class Meta:
        model = TestUrl

    
    def clean_test_url(self):
        if self.cleaned_data["test_url"] is not None:
            if (self.cleaned_data["test_url"].find("/") != 0):
                raise ValidationError("test urls have to start with /")
        return self.cleaned_data["test_url"]


class TestResultAdminInline(admin.TabularInline):
    model = TestResult
    fk_name = "page_url"
    extra = 0
    readonly_fields = ['page_title', 'link_url', 'link_text', 'is_injected', 'created_at']
   
    
  
class TestUrlAdmin(admin.ModelAdmin):
    list_display = ('test_url', 'created_at', 'tested_at')
    actions = ['test_url',
                'delete',
                'export_to_csv',
                'import_public_pathes_from_cms',
                'view_substitution'
    ]
    inlines = [
        TestResultAdminInline,
    ]
    
    form = TestUrlAdminForm
    
    def test_url(self, request, query_set):
        dummy = DummyClient()
        test_date = datetime.now()
        
        for url in query_set:
            self._delete_old_testresults(url)
            sep = "&"
            if url.test_url.find("?") == -1: 
                sep = "?"
            url_no_processing = "%s%s%s=True" % (url.test_url, sep, NO_PROCESSING_GET_PARAM)
            response = dummy.client.get(url_no_processing)
            title, link_tuples = self._extract_links_title(response.content)
            response2 = dummy.client.get(url.test_url)
            title, link_tuples_with_injected = self._extract_links_title(response2.content)
            injested_links = link_tuples_with_injected - link_tuples
            for href, anchor in link_tuples:    
                test_result_obj = TestResult.objects.get_or_create(page_url=url,
                                                 page_title=title.strip(),
                                                 link_url=href,
                                                 link_text=anchor.strip(),
                                                 is_injected=False,
                                                 created_at=test_date
                )
            
            for href, anchor in injested_links:
                test_result_obj = TestResult.objects.get_or_create(page_url=url,
                                                 page_title=title.strip(),
                                                 link_url=href,
                                                 link_text=anchor.strip(),
                                                 is_injected=True,
                                                 created_at=test_date
                )
            
            
            # test done save it
            url.tested_at = test_date
            url.save()
            
            if DUMP_TEST_URLS_FAILURES_TO_STATIC and len(link_tuples) == len(link_tuples_with_injected):
                name1 = "%s_org.html" % (url.id)
                name2 = "%s_injected.html" % (url.id)
                dump_to_static_folderfile(name1, response.content)
                dump_to_static_folderfile(name2, response2.content)
        
        msg = "queried %s urls" % (len(query_set))        
        request.user.message_set.create(message=msg)         
    
    def export_to_csv(self, request, query_set):
        """
        Function to export the link structure to excel
        """
        headline = "id\tpage_url\tpage_title\tlink_anchortext\tlink_href\tis_injected\ttested_at\t \n"
        lines = u"%s" % (headline)
        for url in query_set:
            test_results = TestResult.objects.filter(page_url=url)
            for res in test_results:
                lines += u"%s\t'%s'\t'%s'\t'%s'\t'%s'\t'%s'\t%s\t\n" % (url.id,
                                                                
                                                          url.test_url.strip(),
                                                          res.page_title.strip(),
                                                          res.link_text.strip(),
                                                          res.link_url.strip(),
                                                          res.is_injected,
                                                          res.created_at
                                                          )
                
        response = HttpResponse(content=lines, mimetype="text/csv")
        response['Content-Disposition'] = 'attachment;filename="test_urls_results.csv"'
        return response
    
    def import_public_pathes_from_cms(self, request, query_set):
        #@todo: externalise to settings   
        # act as a plugin here?
        created = 0
        if 'cms' in django_settings.INSTALLED_APPS:
            from cms.models import Page
            from cms.models.titlemodels import Title
            all_test_urls = TestUrl.objects.all().values_list('test_url', flat=True)
            allpublic_pages = Title.objects.filter(page__published=True)
            for x in allpublic_pages:
                if x.path not in all_test_urls:
                    url = u"/%s" % x.path
                    TestUrl.objects.get_or_create(test_url=url)
                    created += 1
            
        msg = "created %s test urls" % (created)        
        request.user.message_set.create(message=msg) 
    
#http://docs.djangoproject.com/en/dev//ref/contrib/admin/actions/#adding-actions-to-the-modeladmin
#http://docs.djangoproject.com/en/dev//ref/contrib/admin/#overriding-admin-templates
    def view_substitution(self, request, query_set):
        
        if query_set and len(query_set) != 1:
            msg = "please mark only one url for preview"        
            request.user.message_set.create(message=msg) 
        else:
            url = reverse("seo_link_check_substitution", kwargs={"test_url_id":query_set[0].id})
            return HttpResponseRedirect(url)
    
    def _extract_links_title(self, html):
        soup = BeautifulSoup(html)
        title = soup.find("title")
        if isinstance(title, Tag):
            title = title.getString()
        else:
            title = ""
        all_links = soup.findAll("a")
        links = set() 
        for a in all_links:
            href = str(a.get('href'))
            anchor = a.getString().strip()
            if (href, anchor) not in links:
                links.add((href, anchor))
        
        return (title, links) 
        
    def _delete_old_testresults(self, url_obj):
        TestResult.objects.filter(page_url=url_obj).delete()
        

admin.site.register(OperatingPath, OperatingPathAdmin)
admin.site.register(ReplacementTemplate, ReplacementTemplateAdmin)
admin.site.register(TargetPath, TargetPathAdmin)
admin.site.register(Term, TermAdmin)
admin.site.register(TestUrl, TestUrlAdmin)

