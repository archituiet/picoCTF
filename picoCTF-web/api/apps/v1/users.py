"""User management endpoints."""
import re
import string

from flask import jsonify
from flask_restplus import Namespace, Resource

import api
from api import PicoException, require_admin

from .schemas import user_req

ns = Namespace('users', description='User management')


@ns.route('')
class UserList(Resource):
    """Get the full list of users, or add a new user."""

    @ns.response(200, 'Success')
    @ns.response(401, 'Not logged in')
    @ns.response(403, 'Not authorized')
    @require_admin
    def get(self):
        """Get the full list of users."""
        return jsonify(api.user.get_all_users())

    @ns.response(201, 'Successfully created user')
    @ns.response(400, 'Error parsing request')
    @ns.response(409, 'Username not available')
    @ns.expect(user_req)
    def post(self):
        """Register a new user."""
        req = user_req.parse_args(strict=True)

        # Do additional validation on request, due to RequestParser
        # limitations (@TODO handle w/ Marshmallow)
        if ('age' not in req['demo'] or
                req['demo']['age'] not in ['13-17', '18+']):
            raise PicoException(
                "'age' must be specified in the 'demo' object. Valid values " +
                "are: ['13-17', '18+']", status_code=400
            )
        if (api.config.get_settings()['email']['parent_verification_email'] and
            req['demo']['age'] != '18+' and (
                'parentemail' not in req['demo'] or not
                re.match(r".+@.+\..{2,}", req['demo']['parentemail']))):
            raise PicoException(
                "Must provide a valid parent email address under the key " +
                "'demo.parentemail'.", status_code=400
            )
        if not all([
                c in string.digits + string.ascii_lowercase for
                c in req['username'].lower()]):
            raise PicoException(
                'Usernames must be alphanumeric.', status_code=400
            )

        # Attempt to create the user
        uid = api.user.add_user(req)

        res = jsonify({
            'success': True,
            'uid': uid
        })
        res.status_code = 201
        return res


@ns.response(200, 'Success')
@ns.response(401, 'Not logged in')
@ns.response(403, 'Not authorized')
@ns.response(404, 'User not found')
@ns.route('/<string:user_id>')
class User(Resource):
    """Get a specific user."""

    @require_admin
    def get(self, user_id):
        """Retrieve a specific user."""
        res = api.user.get_user(uid=user_id)
        if not res:
            raise PicoException('User not found', status_code=404)
        return res, 200
