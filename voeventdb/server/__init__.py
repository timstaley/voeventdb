from ._version import get_versions
__versiondict__ = get_versions()
__version__ = __versiondict__['version']
del get_versions
