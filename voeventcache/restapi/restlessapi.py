from flask.ext.restless import APIManager
from voeventcache.database.models import Voevent

restless_manager = APIManager()
restless_url_prefix = '/restlessv0'
restless_voevent_url = restless_url_prefix + '/voevent'
restless_manager.create_api(
    Voevent,
    url_prefix=restless_url_prefix,
    methods=['GET'],
    exclude_columns=['xml']
)
