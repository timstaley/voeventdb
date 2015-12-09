#!/usr/bin/env python
"""
Initialize the Flask app.
"""
from __future__ import absolute_import, print_function

from sqlalchemy import engine
from flask import Flask, send_from_directory

from voeventdb.server.database import session_registry
from voeventdb.server.restapi.v1.views import apiv1
import voeventdb.server.restapi.v1.filters
from voeventdb.server.restapi.v1.jsonencoder import IsodatetimeJSONEncoder
from voeventdb.server.database.config import testdb_corpus_url

app = Flask(__name__)
app.config.from_object('voeventdb.server.restapi.default_config')
app.register_blueprint(apiv1)


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
        from voeventdb.server import __path__ as server_package_root_dir
        server_package_root_dir = server_package_root_dir[0]
        voeventdb_package_root_dir = os.path.dirname(
            os.path.dirname(server_package_root_dir))
        docs_build_dir = os.path.join(voeventdb_package_root_dir,
                                      'docs', 'build', 'html')
        return send_from_directory(docs_build_dir, filename)


    app.config['APACHE_NODECODE'] = False
    print("Running in debug mode")
    app.run(debug=True)
