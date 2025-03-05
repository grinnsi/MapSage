
import os
from flask import request

def get_app_url_root():
    return request.url_root.removesuffix(os.getenv("DASHBOARD_URL", "dashboard") + "/")