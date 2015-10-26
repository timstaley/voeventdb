from voeventdb.restapi.app import app
rules = [ r for r in sorted(app.url_map.iter_rules())]

print
print "RULES:"
for r in rules:
    print r
print
print "ENDPOINTS"
for r in rules:
    print r.endpoint

