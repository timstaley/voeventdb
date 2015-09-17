#!/usr/bin/env python

from setuptools import setup, find_packages

install_requires = [
    'flask-restless',
    #'flask-restful',
    'iso8601',
    'psycopg2',
    'pytz',
    'SQLAlchemy',
    'voevent-parse',
]

test_requires = [
    'pytest',
    'tox',
]

extras_require = {
    'test': test_requires,
    'all': test_requires,
}
packages = find_packages()
print
print "FOUND PACKAGES: ", packages

setup(
    name="voeventcache",
    version="0.1a0",
    packages=packages,
    package_data={'voeventcache':['tests/resources/*.xml']},
    description="Data-store and accompanying RESTful query API for archiving "
                "and retrieving VOEvent packets.",
    author="Tim Staley",
    author_email="timstaley337@gmail.com",
    url="https://github.com/timstaley/voeventcache",
    install_requires=install_requires,
    extras_require=extras_require
)
