"""Setting related endpoints."""

from flask import jsonify
from flask_restplus import Namespace, Resource

import api
from api import require_admin

from .schemas import settings_patch_req

ns = Namespace('settings', description='View or modify runtime settings')


@ns.route('')
class Settings(Resource):
    """Get or modify the current settings."""

    @require_admin
    @ns.response(200, 'Success')
    @ns.response(401, 'Not logged in')
    @ns.response(403, 'Not authorized')
    def get(self):
        """Get the current settings."""
        return jsonify(api.config.get_settings())

    @require_admin
    @ns.response(200, 'Success')
    @ns.response(400, 'Error parsing request')
    @ns.response(401, 'Not logged in')
    @ns.response(403, 'Unauthorized to change settings')
    @ns.expect(settings_patch_req)
    def patch(self):
        """Update settings."""
        req = {
            k: v for k, v in settings_patch_req.parse_args().items() if
            v is not None
        }
        api.config.change_settings(req)
        return jsonify({
            'success': True
        })
