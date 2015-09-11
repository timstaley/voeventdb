from flask.ext.restless import APIManager
from voeventcache.database.models import Voevent

restless_manager = APIManager()
restless_blueprint = restless_manager.create_api(Voevent,
                                                 url_prefix='/restlessv0',
                                                 methods=['GET'],
                                                 exclude_columns=['xml'])
