
# Number of list entries to return by default
DEFAULT_QUERY_LIMIT = 100
# Maximum number of list-entries returned by a single request:
MAX_QUERY_LIMIT = 10000

# Set this to true when serving via Apache / mod_wsgi,
# and apply the Apache conf setting 'AllowEncodedSlashes NoDecode'.
# This prevents Apache mangling the IVORN path, replacing '//' with '/'.
APACHE_NODECODE = True

# JSONIFY_PRETTYPRINT_REGULAR = False