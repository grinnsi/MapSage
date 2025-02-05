import uvicorn
import os

import server.ogc_apis.features.main as features_api
from server.config import get_logger_config

def start_api_server(debug_mode: bool) -> uvicorn.Server:
    config = uvicorn.Config(
        app=features_api.init_api_server(),
        port=int(os.getenv("APISERVER_PORT", "8000")),
        root_path=os.getenv("APISERVER_ROOT_PATH", ""),
        proxy_headers=True,
        log_config=get_logger_config(debug_mode),
        log_level="debug" if debug_mode else "warning",
        reload=True,
    )
    return uvicorn.Server(config)