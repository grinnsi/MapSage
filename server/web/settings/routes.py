import logging
from flask import Blueprint, request, Response, current_app

from server.web.settings.connections import create_new_connection, get_connections

_LOGGER = logging.getLogger("web.data")

def create_data_endpoints() -> Blueprint:
    bp = Blueprint("database_endpoints", __name__, url_prefix="/data/")
    
    @bp.route('/connections', methods=["GET", "POST", "DELETE"])
    def connections() -> Response:
        request_data = request.get_json() if request.data else ''
        current_app.logger.debug(msg=f"Received following connections request: {request.method} {request_data}")

        if request.method == "GET":
            return get_connections()
        
        if request.method == "POST":
            create_new_connection(request_data)
            return Response(status=200)
        
        if request.method == "DELETE":
            pass

        # Send HTTP Error 501 (Not implemented), when method is neither GET nor POST
        return Response(status=501)
    
    return bp