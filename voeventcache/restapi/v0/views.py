from __future__ import absolute_import

from flask import (
    Blueprint, request, make_response, render_template, current_app
)

import urllib

from voeventcache.database import session_registry as db_session
from voeventcache.database.models import Voevent
import voeventcache.database.convenience as convenience
import voeventcache.database.query as query
from voeventcache.restapi.v0.viewbase import (
    QueryView, ListQueryView, _add_to_api, ResultKeys, PaginationKeys
)
from voeventcache.restapi.v0.errors import (
    IvornNotFound, IvornNotSupplied
)

apiv0 = Blueprint('apiv0', __name__,
                  url_prefix='/apiv0')


def add_to_apiv0(queryview_class):
    """
    Partially bind the 'add_to_api' wrapper so we can use it as a decorator.
    """
    return _add_to_api(queryview_class, apiv0)


def get_apiv0_rules():
    return [r for r in sorted(current_app.url_map.iter_rules())
            if r.endpoint.startswith('apiv0')]


@apiv0.route('/')
def landing_pages():
    """
    API root url. Shows a list of active endpoints.
    """
    docs_url = current_app.config.get('DOCS_URL',
                                      'http://' + request.host + '/docs')
    message = "Welcome to the voeventcache REST API!"
    return render_template('landing.html',
                           message = message,
                           version=apiv0.name,
                           rules=get_apiv0_rules(),
                           docs_url=docs_url,

                           )


@apiv0.errorhandler(IvornNotFound)
@apiv0.errorhandler(IvornNotSupplied)
def ivorn_error(error):
    return render_template('errorbase.html',
                           error=error
                           ), error.code


@apiv0.app_errorhandler(404)
def page_not_found(abort_error):
    docs_url = current_app.config.get('DOCS_URL',
                                      'http://' + request.host + '/docs')
    return render_template('404.html',
                           rules=get_apiv0_rules(),
                           docs_url=docs_url,
                           error=abort_error
                           ), abort_error.code


@add_to_apiv0
class AuthoredMonthCount(QueryView):
    """
    Result:
        Dict: Mapping month -> packet counts per-month.

    Here, 'month' refers to the month of the 'authoring' DateTime,
    i.e. the ``Who.Date`` element of the VOEvent. NB, may be None.


    """
    view_name = 'authored_month_count'

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


@add_to_apiv0
class Count(QueryView):
    """
    Result:
        Int: Number of packets matching querystring.

    Returns total number of packets in database if the querystring is blank.
    """
    view_name = 'count'

    def get_query(self):
        return db_session.query(Voevent)

    def process_query(self, q):
        return q.count()


@add_to_apiv0
class IvornList(ListQueryView):
    """
    Result:
        List: All ivorns matching querystring.
    """
    view_name = 'ivorn'

    def get_query(self):
        return db_session.query(Voevent.ivorn)


@add_to_apiv0
class RoleCount(QueryView):
    """
    Result:
        Dict: Mapping role -> packet counts per-role.
    """
    view_name = 'role_count'

    def get_query(self):
        return query.role_counts_q(db_session)

    def process_query(self, q):
        return dict(q.all())


@add_to_apiv0
class StreamCount(QueryView):
    """
    Result:
        Dict: Mapping stream -> packet counts per-stream.
    """
    view_name = 'stream_count'

    def get_query(self):
        return query.stream_counts_q(db_session)

    def process_query(self, q):
        return dict(q.all())


@add_to_apiv0
class StreamRoleCount(QueryView):
    """
    Result:
        Nested dict: Mapping stream -> role -> packet counts per-stream-and-role.
    """
    view_name = 'stream_role_count'

    def get_query(self):
        return query.stream_counts_role_breakdown_q(db_session)

    def process_query(self, q):
        return convenience.to_nested_dict(q.all())


@apiv0.route('/xml/')
@apiv0.route('/xml/<path:url_encoded_ivorn>')
def get_xml(url_encoded_ivorn=None):
    """
    Returns the XML packet contents stored for a given IVORN.
    """
    # Handle Apache / Debug server difference...
    # Apache conf must include the setting::
    #   AllowEncodedSlashes NoDecode
    # otherwise urlencoded paths have
    # double-slashes ('//') replaced with single-slashes ('/').
    # However, the werkzeug simple-server decodes these by default,
    # resulting in differing dev / production behaviour, which we handle here.

    if url_encoded_ivorn and current_app.config.get('APACHE_NODECODE'):
        ivorn = urllib.unquote(url_encoded_ivorn)
    else:
        ivorn = url_encoded_ivorn
    if ivorn is None:
        raise IvornNotSupplied
    xml = db_session.query(Voevent.xml).filter(
        Voevent.ivorn == ivorn
    ).scalar()
    if xml:
        r = make_response(xml)
        r.mimetype = 'text/xml'
        return r
    else:
        raise IvornNotFound(ivorn)