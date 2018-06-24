
#!/usr/bin/env python

from __future__ import print_function
from setuptools import setup, find_packages
import glob
import versioneer

install_requires = [
    'click',
    'flask',
    'iso8601',
    'psycopg2',
    'pytz',
    'SQLAlchemy',
    'simplejson',
    'voevent-parse>=1.0.1',
    'six',
]

test_requires = [
    'pytest>3',
]

extras_require = {
    'test': test_requires,
    'all': test_requires,
}
packages = find_packages()
print()
print("FOUND PACKAGES: ", packages)

scripts = glob.glob('voeventdb/server/bin/*.py')

classifiers = [
    "License :: OSI Approved :: BSD License",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.6",
    "Intended Audience :: Science/Research",
]

setup(
    name="voeventdb.server",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="Data-store and accompanying RESTful query API for archiving "
                "and retrieving VOEvent packets.",
    author="Tim Staley",
    author_email="github@timstaley.co.uk",
    url="https://github.com/timstaley/voeventdb",
    packages=packages,
    package_data={'voeventdb.server':['tests/resources/*.xml',
                               'restapi/static/css/*/*.css',
                               'restapi/templates/*.html',
                               'restapi/templates/*/*.html',
                               ]},
    install_requires=install_requires,
    extras_require=extras_require,
    scripts=scripts,
    classifiers = classifiers,
)
