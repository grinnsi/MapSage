from logging import getLogger
from flask import Blueprint, request, Response

from server.web.settings.connections import create_new_connection, get_connections

def create_data_endpoints() -> Blueprint:
    bp = Blueprint("database_endpoints", __name__, url_prefix="/data")
    
    @bp.route('/connections', methods=("GET", "POST" ,"DELETE"))
    def connections() -> Response:
        request_data = request.get_json()
        logger = getLogger()
        logger.debug(msg=f"Received following connections request: {request.method} {request_data}")

        if request.method == "GET":
            return get_connections()
        
        if request.method == "POST":
            create_new_connection(request_data)
        
        if request.method == "DELETE":
            pass

        # Send HTTP Error 501 (Not implemented), when method is neither GET nor POST
        return Response(status=501)
    
    return bp