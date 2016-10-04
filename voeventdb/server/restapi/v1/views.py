from __future__ import absolute_import
from flask import (
    Blueprint, request, make_response, render_template, current_app,
    jsonify, url_for
)

from voeventdb.server import __versiondict__ as package_version_dict
from voeventdb.server.restapi.annotate import lookup_relevant_urls
from voeventdb.server.database import session_registry as db_session
from voeventdb.server.database.models import Voevent, Cite, Coord
import voeventdb.server.database.convenience as convenience
import voeventdb.server.restapi.v1.apierror as apierror
import voeventdb.server.database.query as query
from voeventdb.server.restapi.v1.viewbase import (
    QueryView, ListQueryView, _add_to_blueprint, make_response_dict
)
import six
if six.PY3:
    from urllib.parse import unquote
else:
    from urllib import unquote
# This import may look unused, but activates the filter registry -
# Do not delete!
# noinspection PyUnresolvedReferences
import voeventdb.server.restapi.v1.filters

apiv1 = Blueprint('apiv1', __name__,
                  url_prefix='/apiv1')


# First define a few helper functions...

def add_to_apiv1(queryview_class):
    """
    Partially bind the 'add_to_blueprint' wrapper so we can use it as a decorator.
    """
    return _add_to_blueprint(queryview_class, apiv1)


def get_apiv1_rules():
    rules = [r for r in sorted(current_app.url_map.iter_rules(),
                               key=lambda x: str(x))
             if r.endpoint.startswith('apiv1')]
    endpoints_listed = set()
    pruned_rules = []
    for r in rules:
        if r.endpoint not in endpoints_listed:
            pruned_rules.append(r)
            endpoints_listed.add(r.endpoint)
    return pruned_rules


def error_to_dict(error):
    return {
        'error': {
            'code': error.code,
            'description': error.description,
            'message': str(error).replace('\n', '').strip()
        }
    }


def validate_ivorn(url_encoded_ivorn):
    if url_encoded_ivorn and current_app.config.get('APACHE_NODECODE'):
        ivorn = unquote(url_encoded_ivorn)
    else:
        ivorn = url_encoded_ivorn
    if ivorn is None:
        raise apierror.IvornNotSupplied(
            suggested_ivorn_url=url_for(apiv1.name + '.' + ListIvorn.view_name))
    if not convenience.ivorn_present(db_session, ivorn):
        raise apierror.IvornNotFound(
            ivorn,
            suggested_ivorn_url=url_for(apiv1.name + '.' + ListIvorn.view_name))
    return ivorn


# Now root url, error handlers:


@apiv1.route('/')
def apiv1_root_view():
    """
    API root url. Shows a list of active endpoints.
    """
    docs_url = current_app.config.get('DOCS_URL',
                                      'http://' + request.host + '/docs')
    message = "Welcome to the voeventdb REST API, " \
              "interface version '{}'.".format(
        apiv1.name)
    api_details = {
        'message': message,
        'api_version': apiv1.name,
        'git_sha': package_version_dict['full-revisionid'][:8],
        'version_tag': package_version_dict['version'],
        'endpoints': [str(r) for r in get_apiv1_rules()],
        'docs_url': docs_url
    }

    if 'text/html' in request.headers.get("Accept", ""):
        return render_template('landing.html',
                               **api_details
                               )
    else:
        return jsonify(api_details)

@apiv1.errorhandler(apierror.LimitMaxExceeded)
@apiv1.errorhandler(apierror.InvalidQueryString)
@apiv1.errorhandler(apierror.IvornNotFound)
@apiv1.errorhandler(apierror.IvornNotSupplied)
def ivorn_error(error):
    if 'text/html' in request.headers.get("Accept", ""):
        return render_template('errorbase.html',
                               error=error
                               ), error.code
    else:
        return jsonify(error_to_dict(error)), error.code


@apiv1.app_errorhandler(404)
def page_not_found(abort_error):
    if 'text/html' in request.headers.get("Accept", ""):
        docs_url = current_app.config.get('DOCS_URL',
                                          'http://' + request.host + '/docs')
        return render_template('404.html',
                               rules=get_apiv1_rules(),
                               docs_url=docs_url,
                               error=abort_error,
                               endpoints=[str(r) for r in get_apiv1_rules()],
                               ), abort_error.code
    else:
        return jsonify(error_to_dict(abort_error)), abort_error.code


# -----------------------------------------------
# Alphabetically ordered endpoints from here on
# -----------------------------------------------



@add_to_apiv1
class Count(QueryView):
    """
    Result (int):
        Number of packets matching querystring.

    Returns total number of packets in database if the querystring is blank.
    """
    view_name = 'count'

    def get_query(self):
        return db_session.query(Voevent)

    def process_query(self, q):
        return q.count()


@add_to_apiv1
class ListIvorn(ListQueryView):
    """
    Result (list of strings):
        ``[ ivorn1, ivorn2, ... ]``

    List of ivorns matching querystring. Number returned is limited by the
    ``limit`` parameter, which defaults to 100 (see :ref:`pagination`).
    """
    view_name = 'list/ivorn'

    def get_query(self):
        return db_session.query(Voevent.ivorn)

    def process_query(self, query):
        """
        Grab the first entry from every tuple as a single list.
        """
        raw_results = query.all()
        if len(raw_results):
            return list(zip(*raw_results))[0]
        else:
            return raw_results


@add_to_apiv1
class ListIvornReferenceCount(ListQueryView):
    """
    Result (list of 2-element lists):
        ``[[ivorn, n_refs], ...]``

    Get rows containing reference counts. Row entries are

     - IVORN of packet
     - Number of references to other packets, in this packet.
    """
    view_name = 'list/ivorn_nrefs'

    def get_query(self):
        return query.ivorn_cites_to_others_count_q(db_session)

    def process_query(self, query):
        return [tuple(r) for r in query.all()]


@add_to_apiv1
class ListIvornCitedCount(ListQueryView):
    """
    Result (list of 2-element lists):
        ``[[ivorn, n_cited], ...]``

    Get rows containing citation counts. Row entries are:

        - IVORN of packet
        - Number of times this packet is cited by others
    """
    view_name = 'list/ivorn_ncites'

    def get_query(self):
        return query.ivorn_cited_from_others_count_q(db_session)

    def process_query(self, query):
        return [tuple(r) for r in query.all()]


@add_to_apiv1
class MapAuthoredMonthCount(QueryView):
    """
    Result:
        Dict: Mapping month -> packet counts per-month.

    Here, 'month' refers to the month of the 'authoring' DateTime,
    i.e. the ``Who.Date`` element of the VOEvent. NB, may be None.


    """
    view_name = 'map/authored_month_count'

    def get_query(self):
        return query.authored_month_counts_q(db_session)

    def process_query(self, q):
        raw_results = q.all()
        converted_results = []
        for r in raw_results:
            if r.month_id:
                newrow = (r.month_id.date().isoformat()[:-3], r.month_count)
            else:
                newrow = r
            converted_results.append(newrow)
        return dict(converted_results)


@add_to_apiv1
class MapRoleCount(QueryView):
    """
    Result:
        Dict: Mapping role -> packet counts per-role.
    """
    view_name = 'map/role_count'

    def get_query(self):
        return query.role_counts_q(db_session)

    def process_query(self, q):
        return dict(q.all())


@add_to_apiv1
class MapStreamCount(QueryView):
    """
    Result:
        Dict: Mapping stream -> packet counts per-stream.
    """
    view_name = 'map/stream_count'

    def get_query(self):
        return query.stream_counts_q(db_session)

    def process_query(self, q):
        return dict(q.all())


@add_to_apiv1
class MapStreamRoleCount(QueryView):
    """
    Result:
        Nested dict: Mapping stream -> role -> packet counts per-stream-and-role.
    """
    view_name = 'map/stream_role_count'

    def get_query(self):
        return query.stream_counts_role_breakdown_q(db_session)

    def process_query(self, q):
        return convenience.to_nested_dict(q.all())


@apiv1.route('/packet/synopsis/')
@apiv1.route('/packet/synopsis/<path:url_encoded_ivorn>')
def packet_synopsis(url_encoded_ivorn=None):
    """
    Result:
        Nested dict providing key details, e.g.::

            {"coords": [
                            {
                                "dec": 10.9712,
                                "error": 0.05,
                                "ra": 233.7307,
                                "time": "2015-10-01T15:04:22.930000+00:00"
                            },
                            ...
                        ],
             "refs":   [
                            {
                                "cite_type": u"followup",
                                "description": "This is the XRT Position ...",
                                "ref_ivorn": "ivo://nasa.gsfc.gcn/SWIFT#BAT_..."
                            },
                            ...
                        ],
             "voevent": {
                            "author_datetime": "2015-10-01T15:04:46+00:00",
                            "author_ivorn": "ivo://nasa.gsfc.tan/gcn",
                            "ivorn": "ivo://nasa.gsfc.gcn/SWIFT#BAT_GRB_Pos_657286-112",
                            "received": "2015-11-19T20:41:38.226431+00:00",
                            "role": "observation",
                            "stream": "nasa.gsfc.gcn/SWIFT",
                            "version": "2.0"
                        }
             "relevant_urls": [ "http://address1.foo.bar",
                                "http://address2.foo.bar"
                                ]
            }


    Returns some key details for the packet specified by IVORN.

    The required IVORN should be appended to the URL after ``/synopsis/``
    in :ref:`URL-encoded <url-encoding>` form.

    """
    ivorn = validate_ivorn(url_encoded_ivorn)

    voevent_row = db_session.query(Voevent).filter(
        Voevent.ivorn == ivorn).one()

    cites = db_session.query(Cite). \
        filter(Cite.voevent_id == voevent_row.id).all()
    coords = db_session.query(Coord). \
        filter(Coord.voevent_id == voevent_row.id).all()

    v_dict = voevent_row.to_odict(exclude=('id', 'xml'))

    cite_list = [c.to_odict(exclude=('id', 'voevent_id')) for c in cites]
    coord_list = [c.to_odict(exclude=('id', 'voevent_id')) for c in coords]

    relevant_urls = lookup_relevant_urls(voevent_row, cites)

    result = {'voevent': v_dict,
              'refs': cite_list,
              'coords': coord_list,
              'relevant_urls': relevant_urls,
              }

    return jsonify(make_response_dict(result))


@apiv1.route('/packet/xml/')
@apiv1.route('/packet/xml/<path:url_encoded_ivorn>')
def packet_xml(url_encoded_ivorn=None):
    """
    Returns the XML packet contents stored for a given IVORN.

    The required IVORN should be appended to the URL after ``/xml/``
    in :ref:`URL-encoded <url-encoding>` form.
    """
    # Handle Apache / Debug server difference...
    # Apache conf must include the setting::
    #   AllowEncodedSlashes NoDecode
    # otherwise urlencoded paths have
    # double-slashes ('//') replaced with single-slashes ('/').
    # However, the werkzeug simple-server decodes these by default,
    # resulting in differing dev / production behaviour, which we handle here.

    ivorn = validate_ivorn(url_encoded_ivorn)
    xml = db_session.query(Voevent.xml).filter(
        Voevent.ivorn == ivorn
    ).scalar()
    r = make_response(xml)
    r.mimetype = 'text/xml'
    return r
