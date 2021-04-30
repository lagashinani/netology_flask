import flask
import jsonschema
from flask import jsonify, request


def validate(req_schema):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                jsonschema.validate(
                    request.get_json(), schema=req_schema,
                )
            except jsonschema.ValidationError as er:
                resp = flask.make_response(jsonify({'success': False,
                                                    'description': er.message}))
                resp.set_status = 401
                return resp

            result = func(*args, **kwargs)

            return result
        return wrapper
    return decorator


POST = {
    'type': 'object',
    'properties':
        {
            'title': {
                'type': 'string'
            },
            'description': {
                'type': 'string'
            },
        },
    'required': ['title', 'description']
}
