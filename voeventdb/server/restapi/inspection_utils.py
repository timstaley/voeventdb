# Add filters to registry:
import inspect
from voeventdb.server.restapi.v0.filter_base import filter_registry, QueryFilter
from voeventdb.server.restapi.app import app
import voeventdb.server.restapi.v0.views as v0views
from voeventdb.server.restapi.v0.views import QueryView, ListQueryView
import voeventdb.server.restapi.v0.filters as v0filters



def apiv0_endpoints():
    # Grab all app endpoints, filter to apiv0
    apiv0_rules = [r for r in app.url_map.iter_rules()
                   if r.endpoint.startswith('apiv0')]
    # Filter duplicate listings for path-routed endpoints (xml_view, synopsis)
    apiv0_rules = [r for r in apiv0_rules if
                   '<' not in str(r)]
    return {str(r.endpoint)[6:]: str(r) for r in apiv0_rules}


def listqueryview_subclasses():
    return [cls for cls in vars(v0views).values()
            if inspect.isclass(cls)
            and issubclass(cls, ListQueryView)
            and not cls is ListQueryView
            ]

def queryfilter_subclasses():
    return [cls for cls in vars(v0filters).values()
            if inspect.isclass(cls)
            and issubclass(cls, QueryFilter)
            and not cls is QueryFilter
            ]

def queryfilter_keys_and_examples_values():
    filter_classes = queryfilter_subclasses()
    d = { cls.querystring_key: cls.example_values
          for cls in filter_classes }
    return d

def queryview_subclasses():
    return [cls for cls in vars(v0views).values()
            if inspect.isclass(cls)
            and issubclass(cls, QueryView)
            and not cls is QueryView
            ]
