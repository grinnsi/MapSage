import os
from flask import Blueprint, request, Response, current_app

from server.web.settings.connections import create_new_connection, delete_connection, get_connections

def create_data_endpoints() -> Blueprint:
    bp_url_prefix = "/data/"
    # If API is disabled, add /dashboard to the URL prefix, so that the endpoint is always /dashboard/data/...
    if os.getenv("APP_DISABLE_API", "False") == "True":
        bp_url_prefix = "/" + os.getenv("DASHBOARD_URL", "dashboard") + bp_url_prefix

    bp = Blueprint("database_endpoints", __name__, url_prefix=bp_url_prefix)
    
    @bp.route('/connections', methods=["GET", "POST", "DELETE"])
    def connections() -> Response:
        request_data = request.get_json() if request.data else ''
        current_app.logger.debug(msg=f"Received following connections request: {request.method} {request_data}")

        try:
            if request.method == "GET":
                return get_connections()
            
            if request.method == "POST":
                return create_new_connection(request_data)
            
            if request.method == "DELETE":
                return delete_connection(request_data)
        except Exception as e:
            current_app.logger.error(msg=f"Error while processing request: {e}", exc_info=True)
            return Response(status=500, response="Internal server error")

        # Send HTTP Error 501 (Not implemented), when method is not GET, POST or DELETE
        return Response(status=501, response="Method not implemented")
    
    return bp