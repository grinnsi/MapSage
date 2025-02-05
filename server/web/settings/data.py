from flask import Blueprint, request, Response

def create_database_endpoints() -> Blueprint:
    bp = Blueprint("database_endpoints", __name__, url_prefix="/data")
    
    @bp.route('/connections', methods=("GET", "POST" ,"DELETE"))
    def connections() -> Response:
        print(request.form, request.data)
        if request.method == "GET":
            pass
        
        if request.method == "POST":
            pass
        
        if request.method == "DELETE":
            pass

        # Send HTTP Error 501 (Not implemented), when method is neither GET nor POST
        return Response(status=501)
    
    return bp