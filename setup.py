from setuptools import setup, find_packages

seo_link = __import__('seo_link')

readme_file = 'README'
try:
    long_description = open(readme_file).read()
except IOError, err:
    sys.stderr.write("[ERROR] Cannot find file specified as "
        "``long_description`` (%s)\n" % readme_file)
    sys.exit(1)

setup(name='django-seo-link',
      version=seo_link.get_version(),
      description='Internal Linking Silo Structure for massive sites',
      long_description=long_description,
      zip_safe=False,
      author='Frank Bieniek',
      author_email='frank.bieniek@produktlaunch.de',
      url='http://github.com/FrankBie/django-seo-link',
      download_url='http://github.com/FrankBie/django-seo-link/downloads',
      packages = find_packages(exclude=['demo_project', 'demo_project.*']),
      include_package_data=True,
      install_requires = [
        'Django>=1.2.4',
        'BeautifulSoup',
      ],
      test_suite='tests.main',
      classifiers = ['Development Status :: 1 - Alpha',
                     'Environment :: Web Environment',
                     'Framework :: Django',
                     'Intended Audience :: Developers',
                     'License :: OSI Approved :: MIT License',
                     'Operating System :: OS Independent',
                     'Programming Language :: Python',
                     'Topic :: Utilities'],
      )

