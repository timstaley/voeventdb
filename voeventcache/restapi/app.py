#!/usr/bin/env python
"""
Initialize the Flask app.
"""
from __future__ import absolute_import
from voeventcache.database import session_registry
from voeventcache.restapi.v0 import apiv0
from voeventcache.restapi.restlessapi import restless_manager
from voeventcache.tests.config import testdb_scratch_url, testdb_corpus_url
from sqlalchemy import engine
from flask import Flask, render_template, url_for, send_from_directory, request

app = Flask(__name__)
app.config.from_object('voeventcache.restapi.default_config')
app.register_blueprint(apiv0)


# restless_manager.init_app(app, session=session_registry)

# app.config['DOCS_URL'] = "http://127.0.0.1:5000/docs/"

@app.teardown_appcontext
def shutdown_session(exception=None):
    session_registry.remove()


@app.errorhandler(404)
def page_not_found(abort_error):
    rules = [r for r in sorted(app.url_map.iter_rules())
             if r.endpoint.startswith('apiv0')]
    docs_url = app.config.get('DOCS_URL', 'http://' + request.host + '/docs')
    return render_template('404.html',
                           rules=rules,
                           docs_url=docs_url,
                           error=abort_error
                           ), 404


if __name__ == '__main__':
    """
    Run the app in debug mode for development.
    """
    session_registry.configure(bind=engine.create_engine(testdb_corpus_url))


    @app.route('/docs/')
    @app.route('/docs/<path:filename>')
    def serve_docs_in_debug(filename='index.html'):
        import os
        from voeventcache import __path__ as package_root_dir
        package_root_dir = package_root_dir[0]
        docs_build_dir = os.path.join(os.path.dirname(package_root_dir),
                                      'docs', 'build', 'html')
        return send_from_directory(docs_build_dir, filename)

    app.config['APACHE_NODECODE'] = False
    app.run(debug=True)
