#!/usr/bin/env python
"""
Initialize the Flask app.
"""
from __future__ import absolute_import

from sqlalchemy import engine
from flask import Flask, send_from_directory

from voeventdb.database import session_registry
from voeventdb.restapi.v0.views import apiv0
from voeventdb.restapi.v0.jsonencoder import IsodatetimeJSONEncoder
from voeventdb.database.config import testdb_corpus_url

app = Flask(__name__)
app.config.from_object('voeventdb.restapi.default_config')
app.register_blueprint(apiv0)


# restless_manager.init_app(app, session=session_registry)

# app.config['DOCS_URL'] = "http://127.0.0.1:5000/docs/"

@app.teardown_appcontext
def shutdown_session(exception=None):
    session_registry.remove()

app.json_encoder = IsodatetimeJSONEncoder

if __name__ == '__main__':
    """
    Run the app in debug mode for development.
    """
    session_registry.configure(
        bind=engine.create_engine(testdb_corpus_url, echo=True)
    )


    @app.route('/docs/')
    @app.route('/docs/<path:filename>')
    def serve_docs_in_debug(filename='index.html'):
        import os
        from voeventdb import __path__ as package_root_dir
        package_root_dir = package_root_dir[0]
        docs_build_dir = os.path.join(os.path.dirname(package_root_dir),
                                      'docs', 'build', 'html')
        return send_from_directory(docs_build_dir, filename)


    app.config['APACHE_NODECODE'] = False
    app.run(debug=True)
