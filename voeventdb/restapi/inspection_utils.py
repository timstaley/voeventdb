#Add filters to registry:
import voeventdb.restapi.v0.filters
from voeventdb.restapi.v0.filter_base import filter_registry
from voeventdb.restapi.app import app


def list_filter_keys():
    return filter_registry.keys()


def list_apiv0_endpoints():
    # Grab all app endpoints, filter to apiv0
    apiv0_rules = [r for r in app.url_map.iter_rules()
                   if r.endpoint.startswith('apiv0')]
    # Filter duplicate listings for path-routed endpoints (xml_view, synopsis)
    apiv0_rules = [r for r in apiv0_rules if
                   '<' not in str(r)]
    return {str(r.endpoint)[6:]: str(r) for r in apiv0_rules}
