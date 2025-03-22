import os
from flask import Blueprint, request, Response, current_app

from server.ogc_apis.features.implementation import static
from server.web.collections.collections import create_collections, delete_collections, get_all_collections
from server.web.flask_utils import get_app_url_root

def create_collections_endpoints(main_endpoint: str) -> Blueprint:
    bp_url_prefix = main_endpoint + "/collections"
    # If API is disabled, add /dashboard to the URL prefix, so that the endpoint is always /dashboard/data/...
    if os.getenv("APP_DISABLE_API", "False") == "True":
        bp_url_prefix = "/" + os.getenv("DASHBOARD_URL", "dashboard") + bp_url_prefix

    bp = Blueprint("collections_endpoints", __name__, url_prefix=bp_url_prefix)
    
    @bp.route('/', methods=["GET", "POST", "DELETE"])
    def collections() -> Response:
        request_data = request.get_json() if request.data else None

        try:
            if request.method == "GET":
                return get_all_collections()
            
            if request.method == "POST":
                if request_data is None:
                    return Response(status=400, response="Bad request")
                
                if "layer_name" in request_data:
                    response = create_collection(request_data, return_object=False)
                else:
                    response = create_collections(request_data)
                static.collections.update_database_object(app_base_url=get_app_url_root())
                return response
            
            if request.method == "DELETE":
                if request_data is None:
                    return Response(status=400, response="Bad request")
                
                response = delete_collections(request_data)
                static.collections.update_database_object(app_base_url=get_app_url_root())
                return response
            
        except Exception as e:
            current_app.logger.error(msg=f"Error while processing request: {e}", exc_info=True)
            return Response(status=500, response="Internal server error")

        # Send HTTP Error 501 (Not implemented), when method is not GET, POST or DELETE
        return Response(status=501, response="Method not implemented")
    
    @bp.route('/dataset-information/<dataset_uuid>', methods=["GET"])
    def dataset_information(dataset_uuid: str) -> Response:
        request_data = request.get_json() if request.data else None

        try:
            if request.method == "GET":
                return get_dataset_layers_information(dataset_uuid)
            
        except Exception as e:
            current_app.logger.error(msg=f"Error while processing request: {e}", exc_info=True)
            return Response(status=500, response="Internal server error")

        # Send HTTP Error 501 (Not implemented), when method is not GET, POST or DELETE
        return Response(status=501, response="Method not implemented")
    
    return bp