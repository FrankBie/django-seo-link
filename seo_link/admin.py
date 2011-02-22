from django.contrib import admin
from django import forms

from seo_link.models import MatchType, Term, TargetPath, ReplacementTemplate,\
    ExcludePath


class ExcludePathAdminForm(forms.ModelForm):
    
    class Meta:
        model = ExcludePath
    
    def __init__(self, *args, **kwds):
        super(ExcludePathAdminForm, self).__init__(*args, **kwds)
        #custom behavour here
        #self.fields['user'].queryset = User.objects.order_by(...)
    
    def clean_pattern(self):
        # @todo: related to the type check if the pattern is valid
        # starts with = beginning with /
        # exact same
        # regex # regex is compileable
        
        #pattern = "^.*%s.*$" % (term.words.strip().rstrip())
        #reg_ex = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
        return self.cleaned_data["pattern"]
    

class ExcludePathAdmin(admin.ModelAdmin):
    list_display = ('name','type','pattern',)
    #inlines = [ MatchTypeInline ]
    form = ExcludePathAdminForm


class ReplacementTemplateAdmin(admin.ModelAdmin):
    list_display = ('name','template_filename',)


class TargetPathAdmin(admin.ModelAdmin):
    list_display = ('name','path')


class TermAdmin(admin.ModelAdmin):
    list_display = ('words','word_count','target_path','replacement_template','is_active')


admin.site.register(ExcludePath, ExcludePathAdmin)
admin.site.register(ReplacementTemplate, ReplacementTemplateAdmin)
admin.site.register(TargetPath, TargetPathAdmin)
admin.site.register(Term, TermAdmin)