from voeventcache.restapi.app import app
rules = [ r for r in sorted(app.url_map.iter_rules())]

for r in rules:
    print r.endpoint
