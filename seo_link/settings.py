# -*- coding: utf-8 -*-
"""Settings of SEO_LINK"""
from django.conf import settings as django_settings

DEBUG =  getattr(django_settings, 'SEO_LINK_DEBUG',False)

# available backends
BACKEND = getattr(django_settings, 'SEO_LINK_BACKEND','seo_link.backends.simple.SimpleBackend')
#BACKEND = getattr(django_settings, 'SEO_LINK_BACKEND','seo_link.backends.simple.SimpleCachedBackend')
#BACKEND = getattr(django_settings, 'SEO_LINK_BACKEND','seo_link.backends.advanced.LXMLBackend')
#BACKEND = getattr(django_settings, 'SEO_LINK_BACKEND','seo_link.backends.advanced.LXMLCachedBackend')

# do not replace content that is inside these entities
# the snippets need to be wrapped in a html entity, otherwise double replacement is possible
IGNORE_HTML_ENTITIES = getattr(django_settings, 'SEO_LINK_IGNORE_HTML_ENTITIES' ,  ['head','style','script','javascript','a','h1','h2','h3','h4','h5','h6','strong','b','i','span'])

# do not replace content that is inside these selectors
# one of the IGNORE_CSS_SCELECTOR_* can be NONE
IGNORE_CSS_SELECTOR_CLASSES = getattr(django_settings, 'SEO_LINK_IGNORE_CSS_SELECTOR_CLASSES' , ['nav','user-nav','footer',] )
IGNORE_CSS_SELECTOR_IDS = getattr(django_settings, 'SEO_LINK_IGNORE_CSS_SELECTOR_IDS' , ['cms_plugin_overlay','cms_toolbar_mini','cms_toolbar_col2','cms_toolbar_pagebutton','cms_toolbar_settingsbutton'] )

# one of the OPERATIONAL_CSS_SELECTOR_* can be NONE
# if OPERATIONAL_CSS_SELECTOR_CLASSES one is NONE work on all elements
# use this value to select the content area you want to operate on
OPERATIONAL_CSS_SELECTOR_CLASSES = getattr(django_settings, 'SEO_LINK_OPERATIONAL_CSS_SELECTOR_CLASSES', ['main',])

# only operate on these id elements
# if this one is None, it does not restrict
# use this value to select the content area you want to operate on
OPERATIONAL_CSS_SELECTOR_IDS  = getattr(django_settings, 'SEO_LINK_OPERATIONAL_CSS_SELECTOR_IDS', None)

#ALL THE OPERATIONAL_CSS * SETTINGS ARE COMBINDE BY OR 
# only operate on these entities
OPERATIONAL_HTML_ENTITIES = getattr(django_settings, 'SEO_LINK_OPERATIONAL_HTML_ENTITIES' ,  ['div','p',])

# min word count
# operate only on terms that have this as minimum word count
# the replacement always starts with the highest wordcount
MIN_TERM_WORD_COUNT = getattr(django_settings, 'SEO_LINK_MIN_TERM_WORD_COUNT' ,  0)

# Limit the injested REPLACEMENT Terms TO A MAXIMUM PER PAGE
# if this is None, no restriction
MAX_DIFFERENT_TERM_REPLACMENT_PER_PAGE = getattr(django_settings, 'SEO_LINK_MAX_DIFFERENT_TERM_REPLACMENT_PER_PAGE' ,  None)

# Operate only when a user is not logged in
# if you want to use the test url in the backend
# this setting needs to be set to FALSE
# if it is to yes, there is no link injesting after a successful login
ACTIVE_ANONYMOUS_USER_ONLY = getattr(django_settings, 'SEO_LINK_ACTIVE_ANONYMOUS_USER_ONLY' ,  False)  

# Replace the found term in the page only one time
REPLACE_ONLY_ONE_TIME_PER_TERM = getattr(django_settings, 'SEO_LINK_REPLACE_ONLY_ONE_TIME_PER_TERM' ,  True) 

# Exclude Path where the app should not work
GLOBAL_EXCLUDE_PATHES = getattr(django_settings, 'SEO_LINK_GLOBAL_EXCLUDE_PATHES' ,  ['/admin',
                                                                                      '/sentry',
                                                                                      '/media',
                                                                                      '/__debug__',
                                                                                      '/search'
                                                                                      '/uploads'
                                                                                      '/static'
                                                                                      ]
)

#Add Timer and Timeroutput to the output
# turn this off for production
TIMER_ON = getattr(django_settings, 'SEO_LINK_TIMER_ON' ,  False)

#no processing get parameter
NO_PROCESSING_GET_PARAM = getattr(django_settings, 'SEO_LINK_NO_PROCESSING_GET_PARAM' ,  'no_seo_link')

# DAU User Protection
NO_ROOT_PROCESSING = getattr(django_settings, 'SEO_LINK_NO_ROOT_PROCESSING' ,  True)

#cacheing
CACHE_KEY_PREFIX = getattr(django_settings, 'SEO_LINK_CACHE_KEY_PREFIX' ,  'seo_link_')
CACHE_DURATION = getattr(django_settings, 'SEO_LINK_CACHE_DURATION' ,  60*60)

#ADMIN URL TEST Feature 
DUMP_TEST_URLS_FAILURES_TO_STATIC = getattr(django_settings, 'SEO_LINK_DUMP_TEST_URLS_FAILURES_TO_STATIC' ,  True)

# ending without slash
# substitution option in admin
PREVIEW_TEST_URL_PREFIX = getattr(django_settings, 'SEO_LINK_PREVIEW_TEST_URL_PREFIX' ,  "http://localhost:8000")

#sometimes the output is not parseable so ignore and log exceptions?
# set this to True for production
IGNORE_EXCEPTIONS_ON = getattr(django_settings, 'SEO_LINK_IGNORE_EXCEPTIONS_ON' ,  True)

# prettify the html before processing
# slows down but helps with broken html output
# default FALSE
LXML_BEAUTIFULSOUP_PRETTIFY = getattr(django_settings, 'SEO_LINK_LXML_BEAUTIFULSOUP_PRETTIFY' ,  False)

# if you have broken and unclean html,
# this cleans the html before processing
# default FALSE
LXML_CLEANER_ON = getattr(django_settings, 'SEO_LINK_LXML_CLEANER_ON' ,  False)
