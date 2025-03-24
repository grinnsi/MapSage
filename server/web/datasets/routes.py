import os
from flask import Blueprint, request, Response, current_app

from server.web.datasets.connections import create_new_connection, delete_connection, get_connections, get_dataset_layers_information

def create_datasets_endpoints(main_endpoint: str) -> Blueprint:
    bp_url_prefix = main_endpoint + "/datasets"
    # If API is disabled, add /dashboard to the URL prefix, so that the endpoint is always /dashboard/data/...
    if os.getenv("APP_DISABLE_API", "False") == "True":
        bp_url_prefix = "/" + os.getenv("DASHBOARD_URL", "dashboard") + bp_url_prefix

    bp = Blueprint("datasets_endpoints", __name__, url_prefix=bp_url_prefix)
    
    @bp.route('/', methods=["GET", "POST"])
    def connections() -> Response:
        request_data = request.get_json() if request.data else None

        try:
            if request.method == "GET":
                return get_connections()
            
            if request.method == "POST":
                if not request_data:
                    return Response(status=400, response="Bad request")
                
                return create_new_connection(request_data)
        except Exception as e:
            current_app.logger.error(msg=f"Error while processing request: {e}", exc_info=True)
            return Response(status=500, response="Internal server error")

        # Send HTTP Error 501 (Not implemented), when method is not GET or POST
        return Response(status=501, response="Method not implemented")
    
    @bp.route('/<dataset_uuid>', methods=["GET", "DELETE"])
    def dataset_information(dataset_uuid: str) -> Response:
        try:
            if request.method == "GET":
                return get_dataset_layers_information(dataset_uuid)
            
            if request.method == "DELETE":
                return delete_connection(dataset_uuid)
        except Exception as e:
            current_app.logger.error(msg=f"Error while processing request: {e}", exc_info=True)
            return Response(status=500, response="Internal server error")

        # Send HTTP Error 501 (Not implemented), when method is not GET or DELETE
        return Response(status=501, response="Method not implemented")    
    
    return bp