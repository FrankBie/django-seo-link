from setuptools import setup, find_packages
import os, fnmatch
import seo_link

media_files = []

for dirpath, dirnames, filenames in os.walk(os.path.join('seo_link', 'media')):
    for filename in filenames:
        filepath = os.path.join(dirpath, filename)
        failed = False
        for pattern in ('*.py', '*.pyc', '*~', '.*', '*.bak', '*.swp*'):
            if fnmatch.fnmatchcase(filename, pattern):
                failed = True
        if failed:
            continue
        media_files.append(os.path.join(*filepath.split(os.sep)[1:]))
        
if seo_link.VERSION[-1] == 'final':
    CLASSIFIERS = ['Development Status :: 5 - Production/Stable']
elif 'beta' in seo_link.VERSION[-1]:
    CLASSIFIERS = ['Development Status :: 4 - Beta']
else:
    CLASSIFIERS = ['Development Status :: 3 - Alpha']

CLASSIFIERS += [
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
]

setup(
    author="Frank Bieniek",
    author_email="seo_link@produktlaunch.de",
    name='django-seo-link',
    version=seo_link.__version__,
    description='An Advanced SEO Link Middleware',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README')).read(),
    url='http://github.com/FrankBie/django-seo-link/',
    download_url='http://github.com/FrankBie/django-seo-link/downloads',
    license='MIT License',
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    install_requires=[
        'Django>=1.2',
        'south>=0.7.2',
    ],
    packages=find_packages(exclude=["example", "example.*","testdata","testdata.*"]),
    package_data={
        'seo_link': [
            'templates/seo_link/*.html',
            'templates/seo_link/*/*.html',
            'fixtures/*.xml'
        ]
    },
    test_suite = "seo_link.tests",
    zip_safe = False
)
