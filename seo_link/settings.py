"""Settings of SEO_LINK"""
from django.conf import settings as django_settings

DEBUG =  getattr(django_settings, 'SEO_LINK_DEBUG',True)

BACKEND = getattr(django_settings, 'SEO_LINK_BACKEND','seo_link.backends.simple.SimpleBackend')
# do not replace content that is inside these entities
# the snippets need to be wrapped in a html entity, otherwise double replacement is possible
IGNORE_HTML_ENTITIES = getattr(django_settings, 'SEO_LINK_IGNORE_HTML_ENTITIES' ,  ['head','style','script','javascript','a','h1','h2','h3','h4','h5','h6','strong','b','i','span'])

# do not replace content that is inside these selectors
# one of the IGNORE_CSS_SCELECTOR_* can be NONE
IGNORE_CSS_SELECTOR_CLASSES = getattr(django_settings, 'SEO_LINK_IGNORE_CSS_SELECTOR_CLASSES' , ['nav','user-nav','footer',] )
IGNORE_CSS_SELECTOR_IDS = getattr(django_settings, 'SEO_LINK_IGNORE_CSS_SELECTOR_IDS' , None )

# one of the OPERATIONAL_CSS_SELECTOR_* can be NONE
# if OPERATIONAL_CSS_SELECTOR_CLASSES one is NONE work on all 
OPERATIONAL_CSS_SELECTOR_CLASSES = getattr(django_settings, 'SEO_LINK_OPERATIONAL_CSS_SELECTOR_CLASSES', ['main',])

# only operate on these id elements
# if this one is None, it does not restrict
OPERATIONAL_CSS_SELECTOR_IDS  = getattr(django_settings, 'SEO_LINK_OPERATIONAL_CSS_SELECTOR_IDS', None)

#ALL THE OPERATIONAL_CSS * SETTINGS ARE COMBINDE BY OR 
# only operate on these entities
OPERATIONAL_HTML_ENTITIES = getattr(django_settings, 'SEO_LINK_OPERATIONAL_HTML_ENTITIES' ,  ['div','p',])

# min word count
# operate only on terms that have this as minimum word count
# the replacement always starts with the highest wordcount
MIN_TERM_WORD_COUNT = getattr(django_settings, 'SEO_LINK_MIN_TERM_WORD_COUNT' ,  0)

# Limit the injested REPLACEMENT Terms TO A MAXIMUM PER PAGE
# if this one is None, no restriction
MAX_DIFFERENT_TERM_REPLACMENT_PER_PAGE = getattr(django_settings, 'SEO_LINK_MAX_DIFFERENT_TERM_REPLACMENT_PER_PAGE' ,  None)

# Operate only when a user is not logged in
ACTIVE_ANONYMOUS_USER_ONLY = getattr(django_settings, 'SEO_LINK_ACTIVE_ANONYMOUS_USER_ONLY' ,  True)  

# Replace the found term in the page only one time
REPLACE_ONLY_ONE_TIME_PER_TERM = getattr(django_settings, 'SEO_LINK_REPLACE_ONLY_ONE_TIME_PER_TERM' ,  False) 

# Exclude Path where the app should not work
GLOBAL_EXCLUDE_PATHES = getattr(django_settings, 'SEO_LINK_GLOBAL_EXCLUDE_PATHES' ,  ['/admin',
                                                                                      '/sentry',
                                                                                      '/media',
                                                                                      '/__debug__',
                                                                                      '/search'
                                                                                      ]
)

#Add Timer and Timeroutput to the log output
TIMER_ON = getattr(django_settings, 'SEO_LINK_TIMER_ON' ,  True)

#no processing get parameter
NO_PROCESSING_GET_PARAM = getattr(django_settings, 'SEO_LINK_NO_PROCESSING_GET_PARAM' ,  'no_seo_link')

#cacheing
CACHE_KEY_PREFIX = getattr(django_settings, 'SEO_LINK_CACHE_KEY_PREFIX' ,  'seo_link_')
CACHE_DURATION = getattr(django_settings, 'SEO_LINK_CACHE_DURATION' ,  60*60)