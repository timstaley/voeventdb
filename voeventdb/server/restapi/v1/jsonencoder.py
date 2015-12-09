"""
Define the json encoder to be used as default by 'jsonify'.

NB, this must be assigned to ``app.json_encoder`` to take effect.
"""
from flask.json import  JSONEncoder as FlaskJSONEncoder
from datetime import datetime


class IsodatetimeJSONEncoder(FlaskJSONEncoder):
    """
    Like default Flask encoder, but datetimes are ISO formatted.
    """

    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return FlaskJSONEncoder.default(self, o)