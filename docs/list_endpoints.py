from voeventcache.restapi.app import app
endpoints = [ r.endpoint for r in app.url_map.iter_rules()]

for ep in endpoints:
    print ep
