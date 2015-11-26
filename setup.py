
#!/usr/bin/env python

from setuptools import setup, find_packages
import glob
import versioneer

install_requires = [
    'flask-restless',
    #'flask-restful',
    'iso8601',
    'psycopg2',
    'pytz',
    'SQLAlchemy',
    'simplejson',
    'voevent-parse>=0.9',
    'six',
]

test_requires = [
    'pytest',
    'pytest-capturelog',
    'tox',
]

extras_require = {
    'test': test_requires,
    'all': test_requires,
}
packages = find_packages()
print
print "FOUND PACKAGES: ", packages


scripts = glob.glob('voeventdb/bin/*.py')

setup(
    name="voeventdb",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="Data-store and accompanying RESTful query API for archiving "
                "and retrieving VOEvent packets.",
    author="Tim Staley",
    author_email="timstaley337@gmail.com",
    url="https://github.com/timstaley/voeventdb",
    packages=packages,
    package_data={'voeventdb':['tests/resources/*.xml']},
    install_requires=install_requires,
    extras_require=extras_require,
    scripts=scripts
)
