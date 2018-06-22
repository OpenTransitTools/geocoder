import os
import sys
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'simplejson',
    'ott.utils',
]
if sys.version_info[:2] < (3, 0):
    requires.extend(['solrpy'])  # sadly, solrpy doesn't work with py 3.x (June 2018) -- TODO remove/replace dependency

extras_require = dict(
    dev=[],
)

setup(
    name='ott.geocoder',
    version='0.1.0',
    description='Open Transit Tools - OTT GeoCoder',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
    ],
    author="Open Transit Tools",
    author_email="info@opentransittools.org",
    dependency_links=[
        'git+https://github.com/OpenTransitTools/utils.git#egg=ott.utils-0.1.0'
    ],
    license="Mozilla-derived (http://opentransittools.com)",
    url='http://opentransittools.com',
    keywords='ott, otp, gtfs, gtfsdb, data, database, services, transit, geocoder',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    extras_require=extras_require,
    tests_require=requires,
    test_suite="ott.geocoder.tests",
    entry_points="""\
        [console_scripts]
        geocode = ott.geocoder.cmdline:main
    """,
)
